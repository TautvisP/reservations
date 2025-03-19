from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('municipality/<int:municipality_id>/', views.MunicipalityDetailAPIView.as_view(), name='municipality_detail'),
    path('date/<str:reservation_date>/', views.DateDetailAPIView.as_view(), name='date_detail'),
    path('service-plans/', views.ServicePlansView.as_view(), name='service_plans'),

    path('reservations/', views.ReservationsAPIView.as_view(), name='reservations'),
    path('add_reservation/', views.ReservationCreateView.as_view(), name='add_reservation'),
    path('edit_reservation/<int:reservation_id>/', views.ReservationUpdateView.as_view(), name='edit_reservation'),
    path('delete_reservation/<int:reservation_id>/', views.ReservationDeleteView.as_view(), name='delete_reservation'),
    path('create_client_reservation/<int:reservation_id>/', views.ClientReservationCreateView.as_view(), name='create_client_reservation'),

    path('admin-reservations/', views.AdminReservationsView.as_view(), name='admin_reservations'),
    path('edit_client_reservation/<int:client_id>/', views.ClientReservationUpdateView.as_view(), name='edit_client_reservation'),
    path('delete_client_reservation/<int:client_id>/', views.ClientReservationDeleteView.as_view(), name='delete_client_reservation'),

    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]