from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reservation, ClientReservation
from .forms import ReservationForm, ClientReservationForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages

def index(request):
    return render(request, 'index.html')

def reservations(request):
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

@login_required
def add_reservation(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You do not have permission to add reservations.'}, status=403)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ReservationForm()
    
    return render(request, 'add_reservation.html', {'form': form})

@login_required
def edit_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You do not have permission to edit reservations.'}, status=403)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=reservation)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ReservationForm(instance=reservation)
    
    return render(request, 'edit_reservation.html', {'form': form, 'reservation': reservation})

@login_required
def delete_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You do not have permission to delete reservations.'}, status=403)
    
    if request.method == 'POST':
        reservation.delete()
        return redirect('index')
    
    return render(request, 'delete_reservation.html', {'reservation': reservation})

def create_client_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        form = ClientReservationForm(request.POST, reservation=reservation)
        if form.is_valid():
            client_reservation = form.save(commit=False)
            client_reservation.reservation = reservation
            client_reservation.save()
            # Remove the selected time from the available times
            reservation.available_times.remove(client_reservation.selected_time)
            reservation.save()
            # Add a success message
            messages.success(request, 'Jūsų rezervacija sėkmingai sukurta!')
            # If it's an AJAX request, return a JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({"status": "success", "message": "Reservation created successfully"})
            return redirect('index')
    else:
        form = ClientReservationForm(reservation=reservation)
    
    return render(request, 'create_client_reservation.html', {'form': form, 'reservation': reservation})


@login_required
def municipality_detail(request, municipality_id):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You do not have permission to view this information.'}, status=403)
    
    reservations = Reservation.objects.filter(municipality=municipality_id)
    data = {
        'reservations': list(reservations.values('date', 'municipality'))
    }
    return JsonResponse(data)

@login_required
def date_detail(request, reservation_date):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You do not have permission to view this information.'}, status=403)
    
    reservations = Reservation.objects.filter(date=reservation_date)
    reservation_details = []
    for reservation in reservations:
        clients = ClientReservation.objects.filter(reservation=reservation)
        client_details = list(clients.values('client_name', 'client_last_name', 'address', 'phone_number', 'trees_count', 'additional_comments', 'trees_under_4m', 'selected_time'))
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


def service_plans(request):
    """View for displaying service plans"""
    return render(request, 'service_plans.html')