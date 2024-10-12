from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def send_booking_status_update(booking_id, status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"booking_status_{booking_id}",
        {
            'type': 'booking_status_update',
            'status': status,
        }
    )

def send_tracking_update(booking_id, latitude, longitude):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"booking_tracking_{booking_id}",
        {
            'type': 'tracking_update',
            'data': {
                'latitude': latitude,
                'longitude': longitude,
            }
        }
    )
