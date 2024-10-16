# booking/tasks.py
from celery import shared_task
from utils.geospatial import find_nearest_drivers
from .models import Booking
from drivers.models import Driver
from django.utils import timezone
from .utils import send_booking_notification

@shared_task
def assign_driver_task(booking_id):
    try:
        booking = Booking.objects.select_related('vehicle_type').get(id=booking_id)
        pickup_coords = {
            'lat': booking.pickup_location.y,
            'lng': booking.pickup_location.x
        }

        nearest_drivers = find_nearest_drivers(
            pickup_lat=pickup_coords['lat'],
            pickup_lng=pickup_coords['lng'],
            vehicle_type_name=booking.vehicle_type.name,
            max_distance_km=100,
            limit=10
        )

        if nearest_drivers.exists():
            for driver in nearest_drivers:
                send_booking_notification(driver.id, booking.id)

            # booking.notification_sent_at = timezone.now()
            booking.save()
        else:
            print('No available drivers nearby. Booking remains pending.')
    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} does not exist.")
    except Exception as e:
        print(f"Error assigning drivers to booking {booking_id}: {e}")
