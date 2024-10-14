from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import RegistrationForm, OTPForm, LoginForm, DriverProfileForm
from .models import User, OTP
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import os
import boto3
from botocore.exceptions import ClientError
import pyotp
from dotenv import load_dotenv
from utils.aws_sns import send_otp
from drivers.models import Driver

load_dotenv()

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST' and 'register' in request.POST:
        form = RegistrationForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            role = form.cleaned_data.get('role')
            existing_user = User.objects.filter(phone_number=phone_number).first()
            if existing_user:
                messages.error(request, "Phone number already registered. Please log in.")
                return redirect('login')
            otp, success = send_otp(phone_number)
            if success:
                request.session['registration_data'] = {
                    'phone_number': phone_number,
                    'role': role,
                }
                messages.success(request, "OTP sent to your phone number.")
                return redirect('verify_otp')
            else:
                messages.error(request, "Failed to send OTP. Please try again.")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def verify_user_otp(request):
    registration_data = request.session.get('registration_data')
    if not registration_data:
        messages.error(request, "No registration data found. Please register again.")
        return redirect('register')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        driver_form = DriverProfileForm(request.POST) if registration_data.get('role') == 'driver' else None
        
        if form.is_valid() and (driver_form is None or driver_form.is_valid()):
            input_otp = form.cleaned_data.get('otp')
            phone_number = registration_data.get('phone_number')
            
            if verify_otp(input_otp, phone_number):
                user = User.objects.create_user(
                    phone_number=phone_number,
                    role=registration_data.get('role'),
                    password=None
                )

                if user.role == 'driver':
                    vehicle_type = driver_form.cleaned_data.get('vehicle_type')
                    license_plate = driver_form.cleaned_data.get('license_plate')
                    Driver.objects.create(
                        user=user,
                        vehicle_type=vehicle_type,
                        license_plate=license_plate
                    )

                login(request, user)
                del request.session['registration_data']  # Clear session data
                messages.success(request, "Registration successful and logged in.")
                return redirect('home')
            else:
                messages.error(request, "Invalid or expired OTP. Please try again.")
    else:
        form = OTPForm()
        driver_form = DriverProfileForm() if registration_data.get('role') == 'driver' else None

    return render(request, 'verify_otp.html', {'form': form, 'driver_form': driver_form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST' and 'login' in request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            phone_number = form.cleaned_data.get('phone_number')
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                otp, success = send_otp(phone_number)
                if success:
                    request.session['login_data'] = {
                        'phone_number': phone_number,
                    }
                    messages.success(request, "OTP sent to your phone number.")
                    return redirect('verify_login_otp')
                else:
                    messages.error(request, "Failed to send OTP. Please try again.")
            else:
                messages.error(request, "Phone number not registered. Please register first.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def verify_login_otp(request):
    login_data = request.session.get('login_data')
    if not login_data:
        messages.error(request, "No login data found. Please log in again.")
        return redirect('login')

    if request.method == 'POST':
        form = OTPForm(request.POST)
        if form.is_valid():
            input_otp = form.cleaned_data.get('otp')
            phone_number = login_data.get('phone_number')

            # if verify_otp(input_otp, phone_number):
            #     user = User.objects.filter(phone_number=phone_number).first()
            #     if user:
            #         login(request, user)
            #         del request.session['login_data']  # Clear session data
            #         messages.success(request, f"Welcome back, {user.phone_number}!")
            #         return redirect('home')
            #     else:
            #         messages.error(request, "User not found.")
            # else:
            #     messages.error(request, "Invalid or expired OTP. Please try again.")
            user = User.objects.filter(phone_number=phone_number).first()
            if user:
                login(request, user)
                del request.session['login_data']
                messages.success(request, f"Welcome back, {user.phone_number}!")
                return redirect('home')
    else:
        form = OTPForm()
    return render(request, 'verify_login_otp.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect('login')

def verify_otp(input_otp, phone_number):
    try:
        otp_record = OTP.objects.filter(
            phone_number=phone_number,
            otp_code=input_otp
        ).latest('created_at')
        
        if not otp_record.is_expired():
            otp_record.delete()  # Delete OTP after successful verification
            return True
        else:
            otp_record.delete()  # Delete expired OTP
            return False
    except OTP.DoesNotExist:
        return False
