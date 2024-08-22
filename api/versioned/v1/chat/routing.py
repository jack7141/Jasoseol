from django.urls import re_path, path

from api.versioned.v1.chat import consumer

websocket_urlpatterns = [
    path("ws/room/<int:room_id>/messages/<str:user_id>", consumer.ChatConsumer.as_asgi()),
]