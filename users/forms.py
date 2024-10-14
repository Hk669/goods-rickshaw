from django import forms
from .models import User
from drivers.models import VehicleType, Driver

class RegistrationForm(forms.ModelForm):
    phone_number = forms.CharField(
        max_length=10, 
        min_length=10, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10-digit phone number'})
    )
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('phone_number', 'role', 'name')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        if len(phone_number) != 10:
            raise forms.ValidationError("Phone number should be 10 digits long.")
        return phone_number

class OTPForm(forms.Form):
    otp = forms.CharField(
        max_length=6, 
        min_length=6, 
        required=True,
        widget=forms.TextInput(attrs={'autocomplete': 'off'})
    )

    def clean_otp(self):
        otp = self.cleaned_data.get('otp')
        if not otp.isdigit():
            raise forms.ValidationError("OTP should contain only digits.")
        return otp

class LoginForm(forms.Form):
    phone_number = forms.CharField(
        max_length=10, 
        min_length=10, 
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Enter 10-digit phone number'})
    )

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        return phone_number

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('name', 'email')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class DriverProfileForm(forms.ModelForm):
    vehicle_type = forms.ModelChoiceField(queryset=VehicleType.objects.all(), required=True)
    license_plate = forms.CharField(max_length=20, required=True)  # Changed from 'license_number' to 'license_plate'

    class Meta:
        model = Driver
        fields = ('vehicle_type', 'license_plate', 'current_location')

    def clean_license_plate(self):
        license_plate = self.cleaned_data.get('license_plate')
        if Driver.objects.filter(license_plate=license_plate).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This license plate is already registered.")
        return license_plate
