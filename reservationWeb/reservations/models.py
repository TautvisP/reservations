from django.db import models
from django.utils.translation import gettext_lazy as _

class Municipality(models.TextChoices):
    ALYTUS = 'ALY', _('Alytus')
    KAUNAS = 'KAU', _('Kaunas')
    PANEVEZYS = 'PAN', _('Panevėžys')
    KLAIPEDA = 'KLA', _('Klaipėda')
    MARIJAMPOLE = 'MAR', _('Marijampolė')
    SIAULIAI = 'SIA', _('Šiauliai')
    TAURAGE = 'TAU', _('Tauragė')
    TELSIAI = 'TEL', _('Telšiai')
    UTENA = 'UTA', _('Utena')
    VILNIUS = 'VIL', _('Vilnius')

class Reservation(models.Model):
    municipality = models.CharField(
        max_length=3,
        choices=Municipality.choices,
        default=Municipality.VILNIUS,
    )
    date = models.DateField()
    available_times = models.JSONField(default=list)

    def __str__(self):
        return f"{self.get_municipality_display()} on {self.date}"

class ClientReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE)
    client_name = models.CharField(max_length=100)
    client_last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    trees_count = models.IntegerField()
    additional_comments = models.TextField(blank=True, null=True)
    trees_under_4m = models.BooleanField(default=False)
    selected_time = models.CharField(max_length=5)

    def __str__(self):
        return f"Reservation for {self.client_name} {self.client_last_name} on {self.reservation.date} in {self.reservation.get_municipality_display()} at {self.selected_time}"