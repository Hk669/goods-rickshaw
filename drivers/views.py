from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from .forms import DriverLocationForm
from .models import Driver
from django.contrib.gis.geos import Point
from booking.models import Booking, Notification
import json
import logging
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from drivers.utils import get_route_data, decimal_to_float
from datetime import datetime
from django.core.cache import cache

logger = logging.getLogger(__name__)


@login_required
def dashboard(request):
    """
    This view is for the drivers to get the dashboard with complete bookings and statistics.
    """
    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        messages.error(request, "Driver profile not found.")
        return redirect('home')

    # Update the driver's statistics
    driver.update_earnings_and_bookings()

    # Fetch all bookings assigned to the driver
    bookings = Booking.objects.filter(driver=driver).all()
    total_completed_bookings = bookings.filter(status='DELIVERED').count()
    pending_bookings = bookings.filter(status__in=['PENDING', 'ASSIGNED', 'EN_ROUTE']).count()
    cancelled_bookings = bookings.filter(status='CANCELLED').count()

    # Serialize bookings data for JSON
    serialized_bookings = []
    for booking in bookings:
        route_data = get_route_data(booking.pickup_location, booking.dropoff_location)
        serialized_bookings.append({
            'id': booking.id,
            'pickup_location': {
                'y': booking.pickup_location.y,
                'x': booking.pickup_location.x
            },
            'dropoff_location': {
                'y': booking.dropoff_location.y,
                'x': booking.dropoff_location.x
            },
            'status': booking.status,
            'price': booking.price,
            'route': route_data,
        })
    
    bookings_json = json.dumps(serialized_bookings, default=decimal_to_float)

    # Prepare data for the charts
    earnings_labels = []
    earnings_data = []
    monthly_labels = []
    monthly_bookings_data = []

    # Group bookings by created date or month to generate earnings overview and performance
    for booking in bookings:
        month = booking.created_at.strftime('%B %Y')
        if month not in monthly_labels:
            monthly_labels.append(month)
            monthly_bookings_data.append(0)
        monthly_bookings_data[monthly_labels.index(month)] += 1
        
        # Add earnings data points (assuming created_at date)
        date = booking.created_at.strftime('%Y-%m-%d')
        if date not in earnings_labels:
            earnings_labels.append(date)
            earnings_data.append(0)
        if booking.status == 'DELIVERED':
            earnings_data[earnings_labels.index(date)] += float(booking.price)

    return render(request, 'drivers/dashboard.html', {
        'current_date': datetime.now().strftime('%Y-%m-%d'),
        'bookings': serialized_bookings,
        'bookings_json': bookings_json,
        'driver': driver,
        'total_earnings': driver.total_earnings,
        'total_completed_bookings': total_completed_bookings,
        'pending_bookings': pending_bookings,
        'cancelled_bookings': cancelled_bookings,
        'earnings_labels': json.dumps(earnings_labels),
        'earnings_data': json.dumps(earnings_data),
        'monthly_labels': json.dumps(monthly_labels),
        'monthly_bookings_data': json.dumps(monthly_bookings_data),
        'completed_bookings': total_completed_bookings,
    })

@login_required
def driver_dashboard(request):
    if request.user.role != 'driver':
        return redirect('home')
    
    driver = request.user.driver
    # Fetch past notifications, ordered by latest
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]
    
    return render(request, 'drivers/driver_dashboard.html', {'notifications': notifications})


@login_required
def get_current_booking(request):
    """
    this view is for the drivers to get the current booking
    """
    try:
        driver = request.user.driver
    except Driver.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Driver profile not found.'}, status=404)

    booking = Booking.objects.filter(driver=driver).exclude(status__in=['DELIVERED', 'CANCELLED']).first()
    if booking:
        route_data = get_route_data(booking.pickup_location, booking.dropoff_location)
        serialized_booking = [{
            'id': booking.id,
            'pickup_location': {
                'y': booking.pickup_location.y,
                'x': booking.pickup_location.x
            },
            'dropoff_location': {
                'y': booking.dropoff_location.y,
                'x': booking.dropoff_location.x
            },
            'status': booking.status,
            'price': booking.price,
            'route': route_data,
            # Add other necessary fields as needed
        }]
        # print(serialized_booking)
        bookings_json = json.dumps(serialized_booking, default=decimal_to_float)
        return render(request, 'drivers/current_booking.html', {
            'bookings': serialized_booking,
            'bookings_json': bookings_json,
            'driver': driver,
        })
    return render(request, 'drivers/current_booking.html', {'bookings': None, 'driver': driver})


@login_required
@csrf_exempt
def update_location(request):
    if request.method == 'POST' and request.is_ajax():
        form = DriverLocationForm(request.POST)
        if form.is_valid():
            latitude = form.cleaned_data['latitude']
            longitude = form.cleaned_data['longitude']
            try:
                driver = Driver.objects.get(user=request.user)
                driver.current_location = Point(longitude, latitude)
                driver.save()
                return JsonResponse({'status': 'success'})
            except Driver.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': 'Driver profile not found.'}, status=404)
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)


def driver_location(request, driver_id):
    # Fetch the cached location
    location = cache.get(f'driver_{driver_id}_location')
    if location:
        latitude, longitude = location
    else:
        latitude, longitude = None, None  # Default if no data is available

    return render(request, 'drivers/driver_location.html', {
        'latitude': latitude,
        'longitude': longitude,
        'driver_id': driver_id
    })
