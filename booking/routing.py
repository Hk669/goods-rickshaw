from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/bookings/driver/(?P<driver_id>\d+)/$', consumers.DriverBookingConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>\d+)/$', consumers.NotificationConsumer.as_asgi()),
]
