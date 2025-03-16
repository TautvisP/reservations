from django import forms
from .models import Reservation, Municipality, ClientReservation, ServicePlan

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
    
    service_plan = forms.ChoiceField(
        choices=ServicePlan.choices,
        widget=forms.RadioSelect,
        initial=ServicePlan.BASIC,
        label='Paslaugos planas'
    )
    
    trees_count = forms.IntegerField(
        min_value=1,
        max_value=50,
        initial=1,
        label='Augalų skaičius'
    )

    planting_required = forms.ChoiceField(
        choices=[('yes', 'TAIP'), ('no', 'NE')],
        label='Ar bus reikalingas augalų sodinimas ir augalų pristatymas iš manomedelynas.lt',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = ClientReservation
        fields = [
            'client_name', 'client_last_name', 'address', 'phone_number',
            'trees_count', 'additional_comments', 'trees_under_4m', 'selected_time',
            'service_plan', 'planting_required'
        ]
        labels = {
            'client_name': 'Vardas',
            'client_last_name': 'Pavardė',
            'address': 'Adresas',
            'phone_number': 'Telefono numeris',
            'trees_count': 'Augalų skaičius',
            'additional_comments': 'Papildomi komentarai',
            'trees_under_4m': 'Visi augalai iki 4m. aukščio',
            'selected_time': 'Pasirinktas laikas',
            'service_plan': 'Paslaugos planas',
            'planting_required': 'Ar bus reikalingas augalų sodinimas ir augalų pristatymas iš manomedelynas.lt'

        }
        widgets = {
            'client_name': forms.TextInput(attrs={'placeholder': 'Įveskite vardą'}),
            'client_last_name': forms.TextInput(attrs={'placeholder': 'Įveskite pavardę'}),
            'address': forms.TextInput(attrs={'placeholder': 'Įveskite adresą'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '+3706XXXXXXX'}),
            'additional_comments': forms.Textarea(attrs={'placeholder': 'Įveskite papildomus komentarus', 'rows': 3}),
        }
        help_texts = {
            'trees_under_4m': 'Pažymėkite, jei visi augalai yra žemaūgiai arba vidutinio audumo (iki 4 metrų aukščio)',
        }

    def __init__(self, *args, **kwargs):
        reservation = kwargs.pop('reservation', None)
        super().__init__(*args, **kwargs)
        if reservation:
            # Start with placeholder
            choices = [('', 'Pasirinkite laiką')]
            
            # Add all times regardless of type
            if hasattr(reservation, 'available_times') and reservation.available_times:
                if isinstance(reservation.available_times, str):
                    times = [t.strip() for t in reservation.available_times.split(',')]
                else:
                    times = list(reservation.available_times)
                
                for time in times:
                    if time:  # Skip empty strings
                        choices.append((time, time))
            
            # Add contact option
            choices.append(('contact_me', 'Dėl laiko susisieksime'))
            
            # Set choices
            self.fields['selected_time'].choices = choices