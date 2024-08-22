
from django.urls import re_path, path

from api.versioned.v1.status import consumer

websocket_urlpatterns = [
    path("ws/healthcheck", consumer.PingConsumer.as_asgi()),
]