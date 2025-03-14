from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    name = models.CharField(max_length=100)
    county = models.ForeignKey(County, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Reservation(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.municipality.name} on {self.date}"