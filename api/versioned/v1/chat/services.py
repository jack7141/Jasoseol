from channels.db import database_sync_to_async

from api.bases.chat.models import ChatRoom, ChatRoomParticipant
from api.bases.user.models import User
from common.middleware import RedisCacheASGIMiddleware

class ChatService:
    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id
        self.redis_middleware = RedisCacheASGIMiddleware(None)

    @database_sync_to_async
    def check_room_exists(self):
        return ChatRoom.room_exists(self.room_id)

    @database_sync_to_async
    def get_user(self):
        return User.objects.get(id=self.user_id)

    @database_sync_to_async
    def add_user_to_room(self):
        return ChatRoomParticipant.add_user_to_room(self.room_id, self.user_id)

    @database_sync_to_async
    def get_connected_users_count(self):
        return ChatRoomParticipant.get_connected_users_count(self.room_id)

    @database_sync_to_async
    def remove_user_from_room(self):
        return ChatRoomParticipant.remove_user_from_room(self.room_id, self.user_id)

    @database_sync_to_async
    def update_user_last_active(self):
        user = User.objects.get(id=self.user_id)
        user.update_last_active()

    async def get_previous_messages(self):
        return await self.redis_middleware.get_previous_messages(self.room_id)
