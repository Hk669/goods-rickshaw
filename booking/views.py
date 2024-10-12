# views.py
from django.shortcuts import render, redirect
from .models import Booking
from .forms import BookingForm

def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.distance = request.POST.get('distance')
            booking.estimated_time = request.POST.get('estimated_time')
            booking.estimated_price = calculate_price(float(booking.distance))
            booking.save()
            return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm()
    return render(request, 'bookings/create_booking.html', {'form': form})

def calculate_price(distance):
    # Example calculation, e.g., $2 per km
    base_rate = 2.0
    return round(base_rate * distance, 2)
