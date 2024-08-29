
import json

import arrow
import redis
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.core.cache import cache

class RedisCacheASGIMiddleware:
    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        if scope['type'] == 'websocket':
            return await self.websocket_middleware(scope, receive, send)
        return await self.inner(scope, receive, send)

    async def websocket_middleware(self, scope, receive, send):
        async def wrapped_receive():
            message = await receive()
            if message['type'] == 'websocket.receive':
                await self.cache_message(scope, message)
            return message

        async def wrapped_send(message):
            if message['type'] == 'websocket.send':
                await self.cache_message(scope, message)
            await send(message)

        return await self.inner(scope, wrapped_receive, wrapped_send)

    async def cache_message(self, scope, message):
        if 'text' in message:
            try:
                data = json.loads(message['text'])
                path_parts = scope['path'].split('/')
                if len(path_parts) > 3:
                    room_name = path_parts[3]
                    user_id = path_parts[-1]
                    if 'message' in data and 'username' in data:
                        key = f"chat:{room_name}:messages"
                        cached_messages = await sync_to_async(cache.get)(key, [])
                        cache_data = json.dumps({
                            'room_id': room_name,
                            'user_id': user_id,
                            'username': data['username'],
                            'message': data['message'],
                            'created_at': arrow.now("Asia/Seoul").isoformat()
                        })
                        cached_messages.append(cache_data)
                        await database_sync_to_async(cache.set)(key, cached_messages, timeout=None)
            except json.JSONDecodeError:
                pass

    async def get_cached_messages(self, room_name, count=50):
        key = f"chat:{room_name}:messages"
        messages = await database_sync_to_async(cache.get)(key, [])
        return [json.loads(msg) for msg in messages]


    async def get_previous_messages(self, room_id, last_message_id=None, count=50):
        cached_messages = await self.get_cached_messages(room_id, count)
        # if len(cached_messages) < count:
        #     db_messages = await self.get_db_messages(room_id, last_message_id, count - len(cached_messages))
        #     messages = cached_messages + db_messages
        # else:
        #     messages = cached_messages
        return cached_messages