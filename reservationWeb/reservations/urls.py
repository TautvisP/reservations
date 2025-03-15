from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.index, name='index'),
    path('municipality/<int:municipality_id>/', views.municipality_detail, name='municipality_detail'),
    path('date/<str:reservation_date>/', views.date_detail, name='date_detail'),
    path('reservations/', views.reservations, name='reservations'),
    path('add_reservation/', views.add_reservation, name='add_reservation'),
    path('edit_reservation/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
    path('delete_reservation/<int:reservation_id>/', views.delete_reservation, name='delete_reservation'),
    path('create_client_reservation/<int:reservation_id>/', views.create_client_reservation, name='create_client_reservation'),
    path('service-plans/', views.service_plans, name='service_plans'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]