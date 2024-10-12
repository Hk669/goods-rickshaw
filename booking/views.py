from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from utils.geospatial import find_nearest_drivers, calculate_estimated_price, geocode_address
from .models import Booking, Driver, VehicleType
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from logistics_platform.services import send_booking_status_update, send_tracking_update

# @login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            pickup_address = form.cleaned_data['pickup_address']
            dropoff_address = form.cleaned_data['dropoff_address']
            vehicle_type = form.cleaned_data['vehicle_type']

            # Geocode addresses to get coordinates
            # You can use Google Geocoding API or other services
            pickup_coords = geocode_address(pickup_address)
            dropoff_coords = geocode_address(dropoff_address)

            if not pickup_coords or not dropoff_coords:
                messages.error(request, 'Failed to geocode addresses. Please try again.')
                return render(request, 'bookings/create_booking.html', {'form': form})

            # Find nearest drivers
            nearest_drivers = find_nearest_drivers(
                pickup_lat=pickup_coords['lat'],
                pickup_lng=pickup_coords['lng'],
                vehicle_type_name=vehicle_type.name
            )

            # Calculate price and distance
            estimate = calculate_estimated_price(
                pickup_lat=pickup_coords['lat'],
                pickup_lng=pickup_coords['lng'],
                dropoff_lat=dropoff_coords['lat'],
                dropoff_lng=dropoff_coords['lng'],
                vehicle_type=vehicle_type
            )

            if not estimate:
                messages.error(request, 'Failed to calculate price. Please try again.')
                return render(request, 'bookings/create_booking.html', {'form': form})

            # Create booking
            booking = Booking.objects.create(
                user=request.user,
                vehicle_type=vehicle_type,
                pickup_address=pickup_address,
                dropoff_address=dropoff_address,
                pickup_location=Point(pickup_coords['lng'], pickup_coords['lat'], srid=4326),
                dropoff_location=Point(dropoff_coords['lng'], dropoff_coords['lat'], srid=4326),
                distance_km=estimate['distance_km'],
                estimated_time_min=estimate['travel_time_min'],
                price=estimate['estimated_price'],
                status='PENDING'
            )

            # Assign nearest driver if available
            if nearest_drivers:
                assigned_driver = nearest_drivers.first()
                booking.driver = assigned_driver
                booking.status = 'ASSIGNED'
                booking.save()

                # Update driver availability
                assigned_driver.is_available = False
                assigned_driver.save()

                # Optionally, notify the driver via email/SMS

                messages.success(request, f'Booking created and driver {assigned_driver.user.username} assigned.')
            else:
                messages.info(request, 'No available drivers nearby. Your booking is pending.')

            return redirect('booking_detail', booking_id=booking.id)
    else:
        form = BookingForm()

    return render(request, 'bookings/create_booking.html', {'form': form})


# @login_required
def booking_detail(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'bookings/booking_detail.html', {'booking': booking})


# @login_required
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST' and request.is_ajax():
        new_status = request.POST.get('status')
        valid_statuses = [choice[0] for choice in Booking.STATUS_CHOICES]
        if new_status in valid_statuses:
            booking.status = new_status
            booking.save()

            # Send WebSocket update
            send_booking_status_update(booking.id, new_status)

            return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid status.'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)



# @login_required
# def update_location(request):
#     if request.method == 'POST' and request.is_ajax():
#         form = DriverLocationForm(request.POST)
#         if form.is_valid():
#             latitude = form.cleaned_data['latitude']
#             longitude = form.cleaned_data['longitude']
#             try:
#                 driver = Driver.objects.get(user=request.user)
#                 driver.current_location = Point(longitude, latitude)
#                 driver.save()

#                 # Find bookings assigned to this driver that are not yet delivered
#                 bookings = Booking.objects.filter(driver=driver, status__in=['ASSIGNED', 'EN_ROUTE'])

#                 for booking in bookings:
#                     send_tracking_update(booking.id, latitude, longitude)

#                 return JsonResponse({'status': 'success'})
#             except Driver.DoesNotExist:
#                 return JsonResponse({'status': 'error', 'message': 'Driver profile not found.'}, status=404)
#         else:
#             return JsonResponse({'status': 'error', 'message': 'Invalid data.'}, status=400)
#     return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)