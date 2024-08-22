import datetime
import uuid
import arrow

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json

from django.core.cache import cache

from api.bases.chat.models import ChatRoom, ChatRoomParticipant
from common.exceptions import ExpiredApiCacheData
from common.utils import CacheDataManager
from api.bases.user.models import User

import logging


logger = logging.getLogger(__name__)


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f"chat_room_{self.room_id}"
            if not await self.check_room_exists(self.room_id):
                raise ValueError('Chat room does not exist.')

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            self.user = await self.get_user_or_404(user_id)

            await self.add_user_to_room(self.room_id, self.user.id)

            connected_users_count = await self.get_connected_users_count(self.room_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_join',
                    'username': self.user.username,
                    'connected_users_count': connected_users_count
                }
            )
        except ValueError as e:
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
        try:
            group_name = self.get_group_name(self.room_id)
            await self.channel_layer.group_discard(group_name, self.channel_name)

            await self.remove_user_from_room(self.room_id, self.user.id)

            connected_users_count = await self.get_connected_users_count(self.room_id)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_leave',
                    'username': self.user.username,
                    'connected_users_count': connected_users_count
                }
            )
        except Exception as e:
            logger.error(f'Error in disconnect: {str(e)}')



    async def receive_json(self, content):
        message = content['message']

        redis_message = {
            'room_id': self.room_id,
            'user_id': self.user.id,
            'sender_name': self.user.username,
            'message': message,
            'created_at': datetime.datetime.now().isoformat()
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
            }
        )

    async def user_join(self, event):
        username = event['username']
        connected_users_count = event['connected_users_count']
        await self.send_json({
            "type": "user_join",
            "message": f"{username} has joined the chat.",
            "connected_users_count": connected_users_count
        })

    async def user_leave(self, event):
        username = event['username']
        connected_users_count = event['connected_users_count']
        await self.send_json({
            "type": "user_leave",
            "message": f"{username} has left the chat.",
            "connected_users_count": connected_users_count
        })

    async def recieve_group_message(self, event):
        try:
            message = event['message']
            await self.send_json({'message': message, 'sender_name': self.user.username})
        except Exception as e:
            await self.send_json({'error': '메시지 전송 실패'})

    @staticmethod
    def get_group_name(room_id):
        return f"chat_room_{room_id}"

    @database_sync_to_async
    def check_room_exists(self, room_id):
        return ChatRoom.objects.filter(id=room_id).exists()

    @database_sync_to_async
    def get_user_or_404(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise ValueError('User does not exist.')


    @database_sync_to_async
    def add_user_to_room(self, room_id, user_id):
        room = ChatRoom.objects.get(id=room_id)
        ChatRoomParticipant.objects.update_or_create(
            user_id=user_id,
            chat_room=room,
            defaults={'joined_at': arrow.now("Asia/Seoul").datetime}
        )

    @database_sync_to_async
    def get_connected_users_count(self, room_id):
        thirty_minutes_ago = arrow.now("Asia/Seoul").shift(minutes=-30).datetime
        return ChatRoomParticipant.objects.filter(chat_room=room_id, joined_at__gte=thirty_minutes_ago).count()

    @database_sync_to_async
    def remove_user_from_room(self, room_id, user_id):
        ChatRoomParticipant.objects.filter(user=user_id, chat_room=room_id).delete()