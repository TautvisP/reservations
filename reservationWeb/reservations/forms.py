from django import forms
from .models import Reservation, Municipality, ClientReservation

class ReservationForm(forms.ModelForm):
    available_times = forms.MultipleChoiceField(
        choices=[(f"{hour:02d}:00", f"{hour:02d}:00") for hour in range(7, 23)],
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Available Times'
    )

    class Meta:
        model = Reservation
        fields = ['municipality', 'date', 'available_times']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ClientReservationForm(forms.ModelForm):
    selected_time = forms.ChoiceField(
        choices=[],
        required=True,
        label='Select Time'
    )

    class Meta:
        model = ClientReservation
        fields = [
            'client_name', 'client_last_name', 'address', 'phone_number',
            'trees_count', 'additional_comments', 'trees_under_4m', 'selected_time'
        ]
        widgets = {
            'trees_under_4m': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        if reservation:
            self.fields['selected_time'].choices = [(time, time) for time in reservation.available_times]