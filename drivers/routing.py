# drivers/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/drivers/location/$', consumers.DriverLocationConsumer.as_asgi()),
]
