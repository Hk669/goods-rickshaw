from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import BookingForm
from utils.geospatial import find_nearest_drivers, calculate_estimated_price, geocode_address, assign_driver_to_booking
from .models import Booking, Driver, VehicleType
from django.contrib import messages
from django.contrib.gis.geos import Point
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from logistics_platform.services import send_booking_status_update, send_tracking_update
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .tasks import assign_driver_task
from .utils import notify_other_drivers, send_booking_cancellation_notification

@login_required
def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            pickup_address = form.cleaned_data['pickup_address']
            dropoff_address = form.cleaned_data['dropoff_address']
            vehicle_type = form.cleaned_data['vehicle_type']

            # Initiate booking creation
            try:
                with transaction.atomic():
                    # Geocode addresses
                    pickup_coords = geocode_address(pickup_address)
                    dropoff_coords = geocode_address(dropoff_address)

                    if not pickup_coords or not dropoff_coords:
                        messages.error(request, 'Failed to geocode addresses. Please try again.')
                        return render(request, 'bookings/create_booking.html', {'form': form})

                    # Calculate estimated price
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

                    # Create booking with status 'PENDING'
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

                    # Assign driver asynchronously
                    # assign_driver_to_booking.delay(booking.id)
                    assign_driver_to_booking(booking.id)

                    messages.success(request, 'Booking created successfully. Assigning a driver...')
                    return redirect('booking_detail', booking_id=booking.id)
            except Exception as e:
                # Log the exception
                print(f"Error creating booking: {e}")
                messages.error(request, 'An unexpected error occurred. Please try again.')
    else:
        form = BookingForm()

    return render(request, 'bookings/create_booking.html', {'form': form})


def assign_driver_to_booking(booking_id):
    assign_driver_task.delay(booking_id)


@csrf_exempt  # Ensure to handle CSRF appropriately in production
@login_required
@require_POST
def accept_booking(request, booking_id):
    booking_id = booking_id
    driver = request.user.driver  # Assuming the driver is linked to the user

    try:
        with transaction.atomic():
            # Lock the booking row to prevent race conditions
            booking = Booking.objects.select_for_update().get(id=booking_id)

            if booking.status != 'PENDING':
                return JsonResponse({'status': 'error', 'message': 'Booking already assigned.'})

            # Assign the booking to the driver
            booking.driver = driver
            booking.status = 'ASSIGNED'
            booking.save()

            # Update driver availability
            driver.is_available = False
            driver.save()

            # Notify other drivers to cancel the booking
            notify_other_drivers(booking_id, exclude_driver_id=driver.id)

            # Notify the user via Channels
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'notifications_{booking.user.id}',
                {
                    'type': 'send_notification',
                    'message': f'Your booking {booking.id} has been assigned to {driver.user.phone_number}.'
                }
            )

            return JsonResponse({'status': 'success', 'message': 'Booking accepted.'})
    except Booking.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Booking does not exist.'}, status=404)
    except Exception as e:
        print(f"Error accepting booking {booking_id}: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred.'}, status=500)


@login_required
def accept_booking_redirect(request, booking_id):
    # You can reuse the accept_booking logic or redirect to a form
    response = accept_booking(request, booking_id)
    return response


@login_required
def booking_detail(request, booking_id):
    if request.user.role == 'user':
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    elif request.user.role == 'driver':
        booking = get_object_or_404(Booking, id=booking_id, driver=request.user.driver)
    else:
        return redirect('home')

    return render(request, 'bookings/booking_detail.html', {'booking': booking})


@login_required
@require_POST
@csrf_exempt
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, driver=request.user.driver)

    new_status = request.POST.get('status')
    if new_status not in dict(Booking.STATUS_CHOICES):
        return JsonResponse({'status': 'error', 'message': 'Invalid status.'})

    booking.status = new_status
    booking.save()

    # Send WebSocket update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"booking_{booking.id}",
        {
            'type': 'status_update',
            'status': booking.get_status_display(),
        }
    )

    return JsonResponse({'status': 'success'})


@login_required(login_url='login')
def check_bookings(request):
    bookings = Booking.objects.filter(user=request.user).all() if request.user.role == 'user' else Booking.objects.filter(driver=request.user.driver).all()
    return render(request, 'bookings/check_bookings.html', {'bookings': bookings})


# cancel the booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Optional: Add permission checks to ensure only authorized users can cancel
    if request.user != booking.user and not request.user.is_staff:
        messages.error(request, "You do not have permission to cancel this booking.")
        return redirect('booking_detail', booking_id=booking.id)

    if booking.status in ['CANCELLED', 'COMPLETED']:
        messages.warning(request, "This booking cannot be cancelled.")
        return redirect('booking_detail', booking_id=booking.id)

    try:
        with transaction.atomic():
            booking.status = 'CANCELLED'
            booking.save()

            # Send cancellation notification to the driver if assigned
            if booking.driver:
                send_booking_cancellation_notification(booking.driver.id, booking.id)

            messages.success(request, "Booking has been cancelled successfully.")
    except Exception as e:
        # Log the exception as needed
        print(f"Error cancelling booking {booking.id}: {e}")
        messages.error(request, "An error occurred while cancelling the booking.")

    return redirect('booking_detail', booking_id=booking.id)

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