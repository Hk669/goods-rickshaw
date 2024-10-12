from django import forms
from .models import Booking, VehicleType

class BookingForm(forms.ModelForm):
    vehicle_type = forms.ModelChoiceField(queryset=VehicleType.objects.all(), required=True)

    class Meta:
        model = Booking
        fields = ['pickup_address', 'dropoff_address', 'vehicle_type']
