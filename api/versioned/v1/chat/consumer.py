import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from .services import ChatService

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f"chat_room_{self.room_id}"
            self.chat_service = ChatService(self.room_id, user_id)

            if not await self.chat_service.check_room_exists():
                raise ValueError('Chat room does not exist.')

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()

            self.user = await self.chat_service.get_user()
            await self.chat_service.add_user_to_room()
            await self.chat_service.update_user_last_active()

            messages = await self.chat_service.get_previous_messages()
            for message in messages:
                await self.send_json(message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_join',
                    'user_id': str(self.user.id),
                    'username': self.user.username,
                    'connected_users_count': await self.chat_service.get_connected_users_count()
                }
            )

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, 'chat_service'):
            await self.chat_service.remove_user_from_room()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_leave',
                    'username': self.user.username,
                    'connected_users_count': await self.chat_service.get_connected_users_count()
                }
            )
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content):
        message = content.get('message')
        if message:
            await self.chat_service.update_user_last_active()
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': str(self.user.id),
                    'username': self.user.username
                }
            )

    async def user_join(self, event):
        await self.send_json({
            "type": "user_join",
            'user_id': event['user_id'],
            "message": f"{event['username']} has joined the chat.",
            "connected_users_count": event['connected_users_count']
        })

    async def user_leave(self, event):
        await self.send_json({
            "type": "user_leave",
            "message": f"{event['username']} has left the chat.",
            "connected_users_count": event['connected_users_count']
        })

    async def chat_message(self, event):
        await self.send_json({
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username']
        })