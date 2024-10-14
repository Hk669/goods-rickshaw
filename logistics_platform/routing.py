# logistics_platform/routing.py

from django.urls import re_path
from drivers.consumers import DriverLocationConsumer
from . import consumers

websocket_urlpatterns = [
    re_path(r'^ws/booking/(?P<booking_id>\d+)/status/$', consumers.BookingStatusConsumer.as_asgi()),
    re_path(r'^ws/booking/(?P<booking_id>\d+)/tracking/$', consumers.BookingTrackingConsumer.as_asgi()),
    re_path(r'^ws/drivers/location/$', DriverLocationConsumer.as_asgi()),
]
