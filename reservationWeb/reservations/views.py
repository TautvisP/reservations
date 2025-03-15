from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Reservation, ClientReservation, Municipality
from django.db.models import Sum, F, DecimalField
from .forms import ReservationForm, ClientReservationForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count
from django.utils import timezone
from datetime import datetime, timedelta


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
            
            # Calculate the price based on form data
            service_plan = form.cleaned_data['service_plan']
            trees_count = form.cleaned_data['trees_count']
            price_per_tree = 25.00 if service_plan == 'premium' else 20.00
            client_reservation.price_per_tree = price_per_tree
            client_reservation.total_price = price_per_tree * trees_count
            
            client_reservation.save()
            
            # Remove the selected time from the available times
            reservation.available_times.remove(client_reservation.selected_time)
            reservation.save()
            
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


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_reservations(request):
    """View for admin to see all client reservations"""
    
    # Get filter parameters from request
    date_range = request.GET.get('date_range', 'upcoming')
    municipality_filter = request.GET.get('municipality', 'all')
    
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
    reservations = reservations.order_by('date', 'municipality')
    
    # Calculate statistics
    total_reservations = Reservation.objects.count()
    upcoming_reservations = Reservation.objects.filter(date__gte=today).count()
    todays_reservations = Reservation.objects.filter(date=today).count()
    total_clients = ClientReservation.objects.count()

    # Calculate total revenue
    total_revenue = ClientReservation.objects.aggregate(
        total=Sum('total_price')  # Use Sum instead of models.Sum
    )['total'] or 0
    
    # Format for display
    total_revenue = int(total_revenue) if total_revenue == int(total_revenue) else total_revenue
    
    # Get list of municipalities for filter dropdown
    municipalities = [(code, name) for code, name in Municipality.choices]
    
    # Set up pagination
    paginator = Paginator(reservations, 10)  # 10 reservations per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'reservations': page_obj,
        'municipalities': municipalities,
        'total_reservations': total_reservations,
        'upcoming_reservations': upcoming_reservations,
        'todays_reservations': todays_reservations,
        'total_clients': total_clients,
        'total_revenue': total_revenue,  # Add this to context
        'is_paginated': page_obj.has_other_pages(),
        'page_obj': page_obj,
    }
    
    return render(request, 'admin_reservations.html', context)