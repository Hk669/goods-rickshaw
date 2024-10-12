import os
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.urls import path
from . import consumers

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'your_project_name.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path("ws/booking/<int:booking_id>/status/", consumers.BookingStatusConsumer.as_asgi()),
            path("ws/booking/<int:booking_id>/tracking/", consumers.BookingTrackingConsumer.as_asgi()),
        ])
    ),
})
