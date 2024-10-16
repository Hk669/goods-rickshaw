# logistics_platform/asgi.py
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
import booking.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logistics_platform.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            booking.routing.websocket_urlpatterns
        )
    ),
})
