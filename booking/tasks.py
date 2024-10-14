# booking/tasks.py
from celery import shared_task
from .models import Booking
from utils.geospatial import find_nearest_drivers, assign_driver_to_booking

@shared_task
def process_booking_assignment(booking_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        drivers = find_nearest_drivers(
            pickup_lat=booking.pickup_location.y,
            pickup_lng=booking.pickup_location.x,
            vehicle_type_name=booking.vehicle_type.name
        )
        assigned_driver = assign_driver_to_booking(booking, drivers)
        if assigned_driver:
            # Notify driver
            send_driver_assignment_notification(assigned_driver, booking)
        else:
            # Handle no available drivers
            handle_no_available_drivers(booking)
    except Booking.DoesNotExist:
        # Log error
        pass

