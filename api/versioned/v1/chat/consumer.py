import logging
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from api.versioned.v1.chat.services import ChatService

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        try:
            self.room_id = self.scope['url_route']['kwargs']['room_id']
            user_id = self.scope['url_route']['kwargs']['user_id']
            self.group_name = f"chat_room_{self.room_id}"

            self.chat_service = ChatService(self.room_id, user_id)
            await self.chat_service.initialize()

            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            messages = await self.chat_service.get_previous_messages()
            for message in messages:
                await self.send_json(message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_join',
                    'user_id': str(self.chat_service.user.id),
                    'username': self.chat_service.user.username,
                    'connected_users_count': await self.chat_service.get_connected_users_count()
                }
            )

        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            await self.close()

    async def disconnect(self, close_code):
        try:
            await self.chat_service.disconnect_user()
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_leave',
                    'username': self.chat_service.user.username,
                    'connected_users_count': await self.chat_service.get_connected_users_count()
                }
            )
        except Exception as e:
            logger.error(f'Error in disconnect: {str(e)}')

    async def receive_json(self, content):
        try:
            message = content.get('message', '').strip()
            if not message:
                return

            await self.chat_service.update_user_activity()
            await self.chat_service.cache_message(message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user_id': str(self.chat_service.user.id),
                    'username': self.chat_service.user.username
                }
            )
        except Exception as e:
            logger.error(f"Error in receive_json: {str(e)}")
            await self.send_json({'error': 'Failed to process message'})

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
