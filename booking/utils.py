# booking/utils.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Booking, Notification
from drivers.models import Driver
from django.template.loader import render_to_string
# booking/utils.py
from django.urls import reverse
import logging

logger = logging.getLogger(__name__)

def send_booking_notification(driver_id, booking_id):
    try:
        driver = Driver.objects.get(id=driver_id)
        booking = Booking.objects.get(id=booking_id)
        channel_layer = get_channel_layer()

        accept_url = reverse('accept_booking')  # Ensure this URL is correctly defined
        message = render_to_string('bookings/notification_email.html', {
            'driver': driver,
            'booking': booking,
        })

        # Alternatively, create a clickable link
        message = f"You have a new booking (ID: {booking.id}). <a href='http://localhost:8000/bookings/{booking.id}/accept/'>Accept</a>"

        async_to_sync(channel_layer.group_send)(
            f'notifications_{driver.user.id}',
            {
                'type': 'send_notification',
                'message': message
            }
        )
    except Driver.DoesNotExist:
        print(f"Driver with ID {driver_id} does not exist.")
    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} does not exist.")
    except Exception as e:
        print(f"Error sending notification to driver {driver_id}: {e}")

# booking/utils.py
def notify_other_drivers(booking_id, exclude_driver_id):
    try:
        booking = Booking.objects.get(id=booking_id)
        # Find drivers who were notified but didn't accept
        notified_drivers = Driver.objects.filter(
            # Assuming you have a way to track which drivers were notified
            # For example, via a ManyToManyField or a separate Notification model
        ).exclude(id=exclude_driver_id)
        print(f"Notified drivers: {notified_drivers}")
        channel_layer = get_channel_layer()

        for driver in notified_drivers:
            async_to_sync(channel_layer.group_send)(
                f'notifications_{driver.user.id}',
                {
                    'type': 'send_notification',
                    'message': f'Booking {booking.id} has been assigned to another driver.'
                }
            )
    except Booking.DoesNotExist:
        print(f"Booking with ID {booking_id} does not exist.")
    except Exception as e:
        print(f"Error notifying other drivers for booking {booking_id}: {e}")


# cancellation notification

def send_booking_cancellation_notification(driver_id, booking_id):
    try:
        driver = Driver.objects.get(id=driver_id)
        booking = Booking.objects.get(id=booking_id)
        channel_layer = get_channel_layer()

        # Render the cancellation message using the template
        message = render_to_string('bookings/notification_cancellation.html', {
            'driver': driver,
            'booking': booking,
        })

        # Create a Notification instance
        Notification.objects.create(
            user=driver.user,
            booking=booking,
            message=message
        )

        # Send the notification via Channels
        async_to_sync(channel_layer.group_send)(
            f'notifications_{driver.user.id}',
            {
                'type': 'send_notification',
                'message': message
            }
        )

        logger.info(f"Cancellation notification sent to driver {driver_id} for booking {booking_id}.")
    except Driver.DoesNotExist:
        logger.warning(f"Driver with ID {driver_id} does not exist.")
    except Booking.DoesNotExist:
        logger.warning(f"Booking with ID {booking_id} does not exist.")
    except Exception as e:
        logger.error(f"Error sending cancellation notification to driver {driver_id}: {e}")