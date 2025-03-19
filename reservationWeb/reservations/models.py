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
    UKMERGE = 'UKM', _('Ukmergė')
    PRIENAI = 'PRN', _('Prienai')

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

class ServicePlan(models.TextChoices):
    BASIC = 'basic', _('Augalo Startas')
    PREMIUM = 'premium', _('Augalo Ilgalaikis')

class ClientReservation(models.Model):
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, related_name='clients')
    client_name = models.CharField(max_length=100)
    client_last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)
    trees_count = models.IntegerField()
    additional_comments = models.TextField(blank=True, null=True)
    trees_under_4m = models.BooleanField(default=False)
    selected_time = models.CharField(max_length=20)
    
    service_plan = models.CharField(
        max_length=10,
        choices=ServicePlan.choices,
        default=ServicePlan.BASIC,
    )
    planting_required = models.CharField(
        max_length=22,
        choices=[
            ('no', 'NE'),
            ('planting_only', 'TAIP, tik sodinimas'),
            ('planting_and_delivery', 'TAIP, augalai su pristatymu ir sodinimas')
        ],
        default='no',
    )

    price_per_tree = models.DecimalField(max_digits=6, decimal_places=2, default=20.00)
    total_price = models.DecimalField(max_digits=8, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.total_price:
            self.calculate_price()
        super().save(*args, **kwargs)
    
    def calculate_price(self):
        self.price_per_tree = 25.00 if self.service_plan == ServicePlan.PREMIUM else 20.00
        self.total_price = self.price_per_tree * self.trees_count

    def __str__(self):
        return f"Reservation for {self.client_name} {self.client_last_name} on {self.reservation.date} in {self.reservation.get_municipality_display()} at {self.selected_time} - {self.total_price}€"