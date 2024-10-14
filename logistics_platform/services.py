# logistics_platform/services.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from celery import shared_task
from django.contrib.auth import get_user_model
import json

User = get_user_model()

@shared_task
def send_booking_status_update_task(booking_id, status):
    channel_layer = get_channel_layer()
    try:
        from booking.models import Booking  # Import here to avoid circular imports
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        group_name = f"user_{user.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'booking_status_update',
                'booking_id': booking_id,
                'status': status,
            }
        )
    except Booking.DoesNotExist:
        pass

@shared_task
def send_tracking_update_task(booking_id, latitude, longitude):
    channel_layer = get_channel_layer()
    try:
        from booking.models import Booking
        booking = Booking.objects.get(id=booking_id)
        user = booking.user
        group_name = f"user_{user.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'tracking_update',
                'booking_id': booking_id,
                'data': {
                    'latitude': latitude,
                    'longitude': longitude,
                }
            }
        )
    except Booking.DoesNotExist:
        pass

def send_booking_status_update(booking_id, status):
    send_booking_status_update_task.delay(booking_id, status)

def send_tracking_update(booking_id, latitude, longitude):
    send_tracking_update_task.delay(booking_id, latitude, longitude)
