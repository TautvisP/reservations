from django import forms
from .models import Reservation, Municipality, County

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['municipality', 'date']

class UserReservationForm(forms.ModelForm):
    county = forms.ModelChoiceField(queryset=County.objects.all(), required=True, label='Apskritis')
    municipality = forms.ModelChoiceField(queryset=Municipality.objects.none(), required=True, label='Savivaldybė')

    class Meta:
        model = Reservation
        fields = ['county', 'municipality', 'date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'county' in self.data:
            try:
                county_id = int(self.data.get('county'))
                self.fields['municipality'].queryset = Municipality.objects.filter(county_id=county_id).order_by('name')
            except (ValueError, TypeError):
                pass  # invalid input from the client; ignore and fallback to empty Municipality queryset
        elif self.instance.pk:
            self.fields['municipality'].queryset = self.instance.county.municipality_set.order_by('name')