from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Municipality, Reservation, County
from .forms import ReservationForm, UserReservationForm
from django.http import JsonResponse
from django.contrib.auth.views import LoginView, LogoutView

def index(request):
    return render(request, 'index.html')

def reservations(request):
    reservations = Reservation.objects.all()
    data = {
        'reservations': list(reservations.values('date', 'municipality__name'))
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

def user_reservation(request):
    if request.method == 'POST':
        form = UserReservationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserReservationForm()
    
    return render(request, 'user_reservation.html', {'form': form})

def load_municipalities(request):
    county_id = request.GET.get('county')
    municipalities = Municipality.objects.filter(county_id=county_id).order_by('name')
    return JsonResponse(list(municipalities.values('id', 'name')), safe=False)

def municipality_detail(request, municipality_id):
    reservations = Reservation.objects.filter(municipality_id=municipality_id)
    data = {
        'reservations': list(reservations.values('date', 'municipality__name'))
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