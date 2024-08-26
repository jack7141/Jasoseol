import arrow
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.bases.chat.models import ChatRoom, Message, ChatRoomParticipant
from api.bases.user.models import User
from api.versioned.v1.chat.serializers import ChatRoomSerializer


class ChatViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()

        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")

        self.chat_room = ChatRoom.objects.create(title="Test Room")

        self.participant1 = ChatRoomParticipant.objects.create(user=self.user1, chat_room=self.chat_room)
        self.participant2 = ChatRoomParticipant.objects.create(user=self.user2, chat_room=self.chat_room)

        self.base_url = 'http://localhost:8000/v1/chat'

    def test_chatroom_list(self):
        response = self.client.get(f'{self.base_url}/')
        chatrooms = ChatRoom.objects.all()
        serializer = ChatRoomSerializer(chatrooms, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_chatroom_create(self):
        data = {
            "title": "New Room"
        }
        response = self.client.post(f'{self.base_url}/', data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ChatRoom.objects.count(), 2)
        self.assertEqual(ChatRoom.objects.last().title, data['title'])

    def test_chatroom_retrieve(self):
        url = f'{self.base_url}/{self.chat_room.pk}'
        response = self.client.get(url)
        serializer = ChatRoomSerializer(self.chat_room)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_chatroom_update(self):
        url = f'{self.base_url}/{self.chat_room.pk}'
        data = {
            "title": "Updated Room"
        }
        response = self.client.put(url, data, format='json')

        self.chat_room.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.chat_room.title, data['title'])

    def test_chatroom_delete(self):
        url = f'{self.base_url}/{self.chat_room.pk}'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ChatRoom.objects.count(), 0)


    def test_unique_participant_constraint(self):
        with self.assertRaises(Exception):
            ChatRoomParticipant.objects.create(user=self.user1, chat_room=self.chat_room)
