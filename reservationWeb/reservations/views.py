from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Reservation, ClientReservation, Municipality
from django.db.models import Sum
from .forms import ReservationForm, ClientReservationForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage


class IndexView(TemplateView):
    template_name = 'index.html'


class ReservationsAPIView(View):
    def get(self, request):
        reservations_data = Reservation.objects.all()
        data = {
            'reservations': [
                {
                    'id': reservation.id,
                    'date': reservation.date,
                    'municipality': reservation.municipality,  # Code
                    'municipality_name': reservation.get_municipality_display()  # Full name
                }
                for reservation in reservations_data
            ]
        }
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ReservationCreateView(CreateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'add_reservation.html'
    success_url = reverse_lazy('index')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'error': 'You do not have permission to add reservations.'}, status=403)
        return super().dispatch(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ReservationUpdateView(UpdateView):
    model = Reservation
    form_class = ReservationForm
    template_name = 'edit_reservation.html'
    pk_url_kwarg = 'reservation_id'
    success_url = reverse_lazy('index')
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'error': 'You do not have permission to edit reservations.'}, status=403)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['reservation'] = self.object
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ReservationDeleteView(DeleteView):
    model = Reservation
    template_name = 'delete_reservation.html'
    pk_url_kwarg = 'reservation_id'
    success_url = reverse_lazy('index')
    context_object_name = 'reservation'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return JsonResponse({'error': 'You do not have permission to delete reservations.'}, status=403)
        return super().dispatch(request, *args, **kwargs)


class ClientReservationCreateView(View):
    template_name = 'create_client_reservation.html'
    
    def get(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        form = ClientReservationForm(reservation=reservation)
        return render(request, self.template_name, {'form': form, 'reservation': reservation})
    
    def post(self, request, reservation_id):
        reservation = get_object_or_404(Reservation, id=reservation_id)
        form = ClientReservationForm(request.POST, reservation=reservation)

        if form.is_valid():
            client_reservation = form.save(commit=False)
            client_reservation.reservation = reservation

            # Calculate the price based on form data
            service_plan = form.cleaned_data['service_plan']
            trees_count = form.cleaned_data['trees_count']
            price_per_tree = 25.00 if service_plan == 'premium' else 20.00
            client_reservation.price_per_tree = price_per_tree
            client_reservation.total_price = price_per_tree * trees_count

            client_reservation.save()

            # Only remove the selected time from available times if it's not 'contact_me'
            selected_time = client_reservation.selected_time
            if selected_time != 'contact_me' and selected_time in reservation.available_times:
                reservation.available_times.remove(selected_time)
                reservation.save()

            # Send email notification
            service_plan_name = "Augalo Ilgalaikis" if service_plan == "premium" else "Augalo Startas"
            time_display = "Susisiekti dėl laiko" if selected_time == 'contact_me' else selected_time

            subject = f"Nauja rezervacija: {client_reservation.client_name} {client_reservation.client_last_name}"
            message = f"""
    Gauta nauja rezervacija!

    Informacija apie klientą:
    - Vardas, Pavardė: {client_reservation.client_name} {client_reservation.client_last_name}
    - Telefonas: {client_reservation.phone_number}
    - Adresas: {client_reservation.address}
    - Data: {reservation.date}
    - Laikas: {time_display}
    - Miestas: {reservation.get_municipality_display()}
    - Pasirinktas planas: {service_plan_name}
    - Augalų skaičius: {trees_count}
    - Bendra suma: {client_reservation.total_price}€
    - Papildomi komentarai: {client_reservation.additional_comments or "-"}
    - Žemaūgiai augalai (iki 3m): {"Taip" if client_reservation.trees_under_4m else "Ne"}

    Linkime geros dienos!
            """

            # Add planting information if available
            if hasattr(client_reservation, 'planting_required'):
                planting_info = {
                    'no': 'Ne',
                    'planting_only': 'TAIP, tik sodinimas',
                    'planting_and_delivery': 'TAIP, augalai su pristatymu ir sodinimas'
                }.get(client_reservation.planting_required, 'Ne')

                message += f"\nAr bus reikalingas augalų sodinimas ir augalų pristatymasiš MANOMEDELYNAS.LT: {planting_info}"

            # Send the email
            try:
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.ADMIN_EMAIL],
                    headers={'Reply-To': settings.DEFAULT_FROM_EMAIL}
                )
                email.send(fail_silently=False)
                print(f"Email notification sent successfully to {settings.ADMIN_EMAIL}")
            except Exception as e:
                print(f"Failed to send email notification: {str(e)}")

            # Add a success message
            messages.success(request, 'Jūsų rezervacija sėkmingai sukurta!')

            # If it's an AJAX request, return a JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    "status": "success", 
                    "message": "Reservation created successfully",
                    "price": float(client_reservation.total_price)
                })
            return redirect('index')

        return render(request, self.template_name, {'form': form, 'reservation': reservation})


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class MunicipalityDetailAPIView(View):
    def get(self, request, municipality_id):
        reservations = Reservation.objects.filter(municipality=municipality_id)
        data = {
            'reservations': list(reservations.values('date', 'municipality'))
        }
        return JsonResponse(data)


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class DateDetailAPIView(View):
    def get(self, request, reservation_date):
        reservations = Reservation.objects.filter(date=reservation_date)
        reservation_details = []
        for reservation in reservations:
            clients = ClientReservation.objects.filter(reservation=reservation)
            client_details = list(clients.values(
                'client_name', 'client_last_name', 'address', 'phone_number', 
                'trees_count', 'additional_comments', 'trees_under_4m', 'selected_time'
            ))
            reservation_details.append({
                'id': reservation.id,
                'date': reservation.date,
                'municipality': reservation.get_municipality_display(),
                'clients': client_details,
                'is_superuser': request.user.is_superuser
            })
        return JsonResponse({'reservations': reservation_details})


class CustomLoginView(LoginView):
    template_name = 'login.html'


class ServicePlansView(TemplateView):
    template_name = 'service_plans.html'


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class AdminReservationsView(ListView):
    template_name = 'admin_reservations.html'
    context_object_name = 'reservations'
    paginate_by = 10
    
    def get_queryset(self):
        # Get filter parameters from request
        date_range = self.request.GET.get('date_range', 'upcoming')
        municipality_filter = self.request.GET.get('municipality', 'all')
        
        # Base query
        reservations = Reservation.objects.all().prefetch_related('clients')
        
        # Apply date filters
        today = timezone.now().date()
        if date_range == 'upcoming':
            reservations = reservations.filter(date__gte=today)
        elif date_range == 'past':
            reservations = reservations.filter(date__lt=today)
        elif date_range == 'today':
            reservations = reservations.filter(date=today)
        elif date_range == 'week':
            end_of_week = today + timedelta(days=(6-today.weekday()))
            reservations = reservations.filter(date__gte=today, date__lte=end_of_week)
        elif date_range == 'month':
            next_month = today.replace(day=1, month=today.month+1) if today.month < 12 else today.replace(day=1, month=1, year=today.year+1)
            reservations = reservations.filter(date__gte=today, date__lt=next_month)
        
        # Apply municipality filter
        if municipality_filter != 'all':
            reservations = reservations.filter(municipality=municipality_filter)
        
        # Calculate totals for each reservation
        for reservation in reservations:
            reservation.total_sum = sum(float(client.total_price) for client in reservation.clients.all())
        
        # Order by date (newest first, then by municipality name)
        return reservations.order_by('date', 'municipality')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        
        # Calculate statistics
        context['total_reservations'] = Reservation.objects.count()
        context['upcoming_reservations'] = Reservation.objects.filter(date__gte=today).count()
        context['todays_reservations'] = Reservation.objects.filter(date=today).count()
        context['total_clients'] = ClientReservation.objects.count()
        
        # Calculate total revenue
        total_revenue = ClientReservation.objects.aggregate(
            total=Sum('total_price')
        )['total'] or 0
        
        # Format for display
        context['total_revenue'] = int(total_revenue) if total_revenue == int(total_revenue) else total_revenue
        
        # Get list of municipalities for filter dropdown
        context['municipalities'] = [(code, name) for code, name in Municipality.choices]
        
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ClientReservationUpdateView(View):
    template_name = 'edit_client_reservation.html'
    
    def get(self, request, client_id):
        client_reservation = get_object_or_404(ClientReservation, id=client_id)
        reservation = client_reservation.reservation
        form = ClientReservationForm(instance=client_reservation, reservation=reservation)
        
        return render(request, self.template_name, {
            'form': form, 
            'client': client_reservation,
            'reservation': reservation
        })
    
    def post(self, request, client_id):
        client_reservation = get_object_or_404(ClientReservation, id=client_id)
        reservation = client_reservation.reservation
        original_time = client_reservation.selected_time
        
        form = ClientReservationForm(request.POST, instance=client_reservation, reservation=reservation)
        if form.is_valid():
            # Get the new selected time before saving
            new_time = form.cleaned_data['selected_time']
            
            # Handle time slot availability updates
            if original_time != new_time:
                # If original time was not 'contact_me', add it back to available times
                if original_time != 'contact_me' and original_time not in reservation.available_times:
                    if isinstance(reservation.available_times, list):
                        reservation.available_times.append(original_time)
                    else:
                        # Handle case where available_times is a string
                        times = reservation.available_times.split(',') if isinstance(reservation.available_times, str) else []
                        times.append(original_time)
                        reservation.available_times = ','.join(times)
                
                # If new time is not 'contact_me', remove it from available times
                if new_time != 'contact_me' and new_time in reservation.available_times:
                    if isinstance(reservation.available_times, list):
                        reservation.available_times.remove(new_time)
                    else:
                        # Handle case where available_times is a string
                        times = reservation.available_times.split(',') if isinstance(reservation.available_times, str) else []
                        if new_time in times:
                            times.remove(new_time)
                        reservation.available_times = ','.join(times)
                
                # Save the reservation with updated available times
                reservation.save()
            
            # Save the client reservation
            form.save()
            
            messages.success(request, 'Kliento rezervacija sėkmingai atnaujinta!')
            return redirect('admin_reservations')
            
        return render(request, self.template_name, {
            'form': form, 
            'client': client_reservation,
            'reservation': reservation
        })


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(lambda u: u.is_superuser), name='dispatch')
class ClientReservationDeleteView(View):
    template_name = 'delete_client_reservation.html'
    
    def get(self, request, client_id):
        client_reservation = get_object_or_404(ClientReservation, id=client_id)
        return render(request, self.template_name, {'client': client_reservation})
    
    def post(self, request, client_id):
        client_reservation = get_object_or_404(ClientReservation, id=client_id)
        
        # If time was taken up, add it back to available times
        if client_reservation.selected_time != 'contact_me':
            reservation = client_reservation.reservation
            if client_reservation.selected_time not in reservation.available_times:
                reservation.available_times.append(client_reservation.selected_time)
                reservation.save()
        
        client_reservation.delete()
        messages.success(request, 'Kliento rezervacija sėkmingai ištrinta!')
        return redirect('admin_reservations')