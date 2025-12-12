"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

# Set DJANGO_SETTINGS_MODULE early so subsequent Django imports work correctly
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

from django.core.asgi import get_asgi_application  # noqa: E402

# Channels ASGI application with WebSocket support
from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402

import mysite.routing  # noqa: E402

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(
            URLRouter(mysite.routing.websocket_urlpatterns)
        ),
    }
)
