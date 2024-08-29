from datetime import timedelta, timezone

import arrow
from django.db import models

from api.bases.user.models import User


class ChatRoom(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_at = models.DateTimeField(auto_now=True)

    @classmethod
    def room_exists(cls, room_id):
        return cls.objects.filter(id=room_id).exists()
    

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_previous_messages(cls, room_id, last_message_id=None, limit=50):
        query = cls.objects.filter(chat_room=room_id).order_by('-created_at')
        if last_message_id:
            last_message = cls.objects.get(id=last_message_id)
            query = query.filter(created_at__lt=last_message.created_at)
        return list(query.values('id', 'content', 'user__username', 'created_at')[:limit])

    def __str__(self):
        return f'{self.user.username}: {self.content[:20]}'



class ChatRoomParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_active = models.DateTimeField(auto_now=True)

    @classmethod
    def add_user_to_room(cls, room_id, user_id):
        room = ChatRoom.objects.get(id=room_id)
        return cls.objects.update_or_create(
            user_id=user_id,
            chat_room=room,
            defaults={'joined_at': arrow.now("Asia/Seoul").datetime}
        )

    @classmethod
    def get_connected_users_count(cls, room_id):
        thirty_minutes_ago = arrow.now("Asia/Seoul").shift(minutes=-30).datetime
        return cls.objects.filter(chat_room=room_id, joined_at__gte=thirty_minutes_ago).count()

    @classmethod
    def remove_user_from_room(cls, room_id, user_id):
        return cls.objects.filter(user=user_id, chat_room=room_id).delete()


    class Meta:
        unique_together = ('user', 'chat_room')