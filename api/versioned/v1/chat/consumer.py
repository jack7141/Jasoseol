import datetime
import uuid
import arrow
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
import json
from django.db import transaction
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from api.bases.chat.models import ChatRoom, ChatRoomParticipant, Message
from common.exceptions import ExpiredApiCacheData
from common.middleware import RedisCacheASGIMiddleware
from api.bases.user.models import User
import logging

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.is_connected = False
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f"chat_room_{self.room_id}"

            if not await self.check_room_exists(self.room_id):
                raise ValueError('Chat room does not exist.')

            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            self.is_connected = True

            self.user = await self.get_user_or_404(user_id)
            await self.add_user_to_room(self.room_id, self.user.id)
            await self.update_user_last_active(self.user.id)

            if self.is_connected:
                self.user = await self.get_user_or_404(user_id)
                await self.update_user_last_active(self.user.id)
                await self.add_user_to_room(self.room_id, self.user.id)

                middleware = RedisCacheASGIMiddleware(None)
                messages = await middleware.get_previous_messages(self.room_id)
                for message in messages:
                    await self.send_json(message)
                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'user_join',
                        'user_id': str(self.user.id),
                        'username': self.user.username,
                        'connected_users_count': await self.get_connected_users_count(self.room_id)
                    }
                )
            logger.error(f"Connection error: {str(e)}")
            if self.is_connected:
                await self.send_json({'error': str(e)})
            await self.close()
        except Exception as e:
            logger.error(f"Unexpected error during connection: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        if self.is_connected:
            try:
                group_name = self.get_group_name(self.room_id)
                await self.channel_layer.group_discard(group_name, self.channel_name)

                # await self.remove_user_from_room(self.room_id, self.user.id)

                await self.channel_layer.group_send(
                    self.group_name,
                    {
                        'type': 'user_leave',
                        'username': self.user.username,
                        'connected_users_count': await self.get_connected_users_count(self.room_id)
                    }
                )
            except Exception as e:
                logger.error(f"Error during disconnect: {str(e)}")
            finally:
                self.is_connected = False

    async def receive_json(self, content):
        if not self.is_connected:
            return

        try:
            message = content.get('message', '').strip()
            if not message:
                return

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'receive_group_message',
                    'message': message,
                    'user_id': str(self.user.id),
                    'username': self.user.username
                }
            )
        except Exception as e:
            logger.error(f"Error in receive_json: {str(e)}")
            if self.is_connected:
                await self.send_json({'error': 'Failed to process message'})

    async def user_join(self, event):
        if self.is_connected:
            await self.send_json({
                "type": "user_join",
                'user_id': event['user_id'],
                "message": f"{event['username']} has joined the chat.",
                "connected_users_count": event['connected_users_count']
            })

    async def user_leave(self, event):
        if self.is_connected:
            await self.send_json({
                "type": "user_leave",
                "message": f"{event['username']} has left the chat.",
                "connected_users_count": event['connected_users_count']
            })

    async def receive_group_message(self, event):
        if self.is_connected:
            try:
                await self.send_json({
                    'message': event['message'],
                    'user_id': event['user_id'],
                    'sender_name': event['username']
                })
            except Exception as e:
                logger.error(f"Error in receive_group_message: {str(e)}")
                if self.is_connected:
                    await self.send_json({'error': 'Failed to send message'})

    async def send_cached_and_previous_messages(self):
        try:
            recent_messages = await self.get_recent_messages_from_cache()
            for message in recent_messages:
                message['user_id'] = str(message['user_id'])
                if self.is_connected:
                    await self.send_json(message)

            previous_messages = await self.get_previous_messages(self.room_id)
            for message in previous_messages:
                if self.is_connected:
                    await self.send_json(message)
        except Exception as e:
            logger.error(f"Error sending cached and previous messages: {str(e)}")

    def get_group_name(self, room_id):
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
    @transaction.atomic
    def add_user_to_room(self, room_id, user_id):
        room = ChatRoom.objects.select_for_update().get(id=room_id)
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
    @transaction.atomic
    def remove_user_from_room(self, room_id, user_id):
        ChatRoomParticipant.objects.filter(user=user_id, chat_room=room_id).delete()

    @database_sync_to_async
    @transaction.atomic
    def update_user_last_active(self, user_id):
        try:
            user = User.objects.select_for_update().get(id=user_id)
            user.last_active = arrow.now('Asia/Seoul').datetime
            user.save()
        except User.DoesNotExist:
            logger.error(f"Failed to update last active: User {user_id} does not exist.")
