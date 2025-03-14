from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reservation, ClientReservation
from .forms import ReservationForm, ClientReservationForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView

def index(request):
    return render(request, 'index.html')

def reservations(request):
    reservations = Reservation.objects.all()
    data = {
        'reservations': list(reservations.values('id', 'date', 'municipality'))
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
            return redirect('index')
    else:
        form = ClientReservationForm(reservation=reservation)
    
    return render(request, 'create_client_reservation.html', {'form': form, 'reservation': reservation})

def municipality_detail(request, municipality_id):
    reservations = Reservation.objects.filter(municipality=municipality_id)
    data = {
        'reservations': list(reservations.values('date', 'municipality'))
    }
    return JsonResponse(data)

def date_detail(request, reservation_date):
    reservations = Reservation.objects.filter(date=reservation_date)
    return render(request, 'date_detail.html', {
        'date': reservation_date,
        'reservations': reservations,
    })

class CustomLoginView(LoginView):
    template_name = 'login.html'