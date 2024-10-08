from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from django.core.cache import cache

from api.bases.chat.models import ChatRoom
from common.exceptions import ExpiredApiCacheData
from common.utils import CacheDataManager


class ChatConsumer(AsyncJsonWebsocketConsumer):
    def receive_json(self, content, **kwargs):
        return

    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            self.group_name = f"chat_room_{self.room_id}"
            if not await self.check_room_exists(self.room_id):
                raise ValueError('Chat room does not exist.')

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            user = self.scope["user"]
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_join',
                    'username': user.username,
                }
            )
        except ValueError as e:
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        try:
            group_name = self.get_group_name(self.room_id)
            await self.channel_layer.group_discard(group_name, self.channel_name)
            username = getattr(self.scope, "username", None)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_leave',
                    'username': username,
                }
            )
        except Exception as e:
            pass


    async def receive_json(self, content):
        message = content['message']
        sender_name = content['sender_name']

        redis_message = {
            'room_id': self.room_id,
            'sender_name': sender_name,
            'message': message
        }
        data_type = 'chat_message'
        unique_key = f'{self.group_name}_messages'

        try:
            cached_messages = CacheDataManager.get_cache(data_type, unique_key)
        except ExpiredApiCacheData:
            cached_messages = []

        cached_messages.append(redis_message)
        CacheDataManager.set_cache(data_type, unique_key, cached_messages)

        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'recieve_group_message',
                'message': message,
                'sender_name': sender_name
            }
        )

    async def user_join(self, event):
        username = event['username']
        await self.send_json({
            "type": "user_join",
            "message": f"{username} has joined the chat."
        })

    async def user_leave(self, event):
        username = event['username']
        await self.send_json({
            "type": "user_leave"
            "message": f"{username} has left the chat."
        })

    async def recieve_group_message(self, event):
        try:
            message = event['message']
            sender_name = event['sender_name']
            await self.send_json({'message': message, 'sender_name': sender_name})
        except Exception as e:
            await self.send_json({'error': '메시지 전송 실패'})

    @staticmethod
    def get_group_name(room_id):
        return f"chat_room_{room_id}"

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return ChatRoom.objects.filter(id=room_id).exists()