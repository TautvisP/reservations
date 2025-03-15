from django import forms
from .models import Reservation, Municipality, ClientReservation

class ReservationForm(forms.ModelForm):
    time_choices = []
    for hour in range(7, 23):
        time_choices.append((f"{hour:02d}:00", f"{hour:02d}:00"))
        time_choices.append((f"{hour:02d}:30", f"{hour:02d}:30"))
    
    available_times = forms.MultipleChoiceField(
        choices=time_choices,
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Galimi laikai'
    )


    class Meta:
        model = Reservation
        fields = ['municipality', 'date', 'available_times']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'municipality': 'Miestas',
            'date': 'Data',
        }

class ClientReservationForm(forms.ModelForm):
    selected_time = forms.ChoiceField(
        choices=[],
        required=True,
        label='Pasirinktas laikas'
    )

    class Meta:
        model = ClientReservation
        fields = [
            'client_name', 'client_last_name', 'address', 'phone_number',
            'trees_count', 'additional_comments', 'trees_under_4m', 'selected_time'
        ]
        labels = {
            'client_name': 'Vardas',
            'client_last_name': 'Pavardė',
            'address': 'Adresas',
            'phone_number': 'Telefono numeris',
            'trees_count': 'Medžių skaičius',
            'additional_comments': 'Papildomi komentarai',
            'trees_under_4m': 'Visi medžiai žemesni nei 4m',
            'selected_time': 'Pasirinktas laikas'
        }
        widgets = {
            'client_name': forms.TextInput(attrs={'placeholder': 'Įveskite vardą'}),
            'client_last_name': forms.TextInput(attrs={'placeholder': 'Įveskite pavardę'}),
            'address': forms.TextInput(attrs={'placeholder': 'Įveskite adresą'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+3706XXXXXXX'}),
            'trees_count': forms.NumberInput(attrs={'placeholder': 'Įveskite medžių skaičių', 'min': '1'}),
            'additional_comments': forms.Textarea(attrs={'placeholder': 'Įveskite papildomus komentarus', 'rows': 4}),
            'trees_under_4m': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        if reservation:
            self.fields['selected_time'].choices = [(time, time) for time in reservation.available_times]
            # Add an empty choice as the first option
            self.fields['selected_time'].choices.insert(0, ('', 'Pasirinkite laiką'))