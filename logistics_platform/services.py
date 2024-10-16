from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Use these functions instead of directly accessing DEFAULT_CHANNEL_LAYER
def send_booking_status_update(booking_id, status):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"booking_{booking_id}",
        {
            "type": "booking.status_update",
            "booking_id": booking_id,
            "status": status,
        },
    )

def send_tracking_update(booking_id, location):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"tracking_{booking_id}",
        {
            "type": "tracking.update",
            "booking_id": booking_id,
            "location": location,
        },
    )
