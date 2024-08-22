"""
WSGI config for api_backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os

from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

from api.versioned.v1.chat import routing as chat_routing
from api.versioned.v1.status import routing as status_routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api_backend.settings')

combined_websocket_urlpatterns = chat_routing.websocket_urlpatterns + \
                                 status_routing.websocket_urlpatterns


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket":
        AuthMiddlewareStack(
            AllowedHostsOriginValidator(
            URLRouter(
                combined_websocket_urlpatterns
            )
        ),
    ),
})