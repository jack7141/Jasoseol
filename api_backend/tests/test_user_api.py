from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from api.bases.user.models import User
from api.versioned.v1.user.serializers import UserSerializer


class UserViewSetTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.base_url = '/v1/user'

    def test_user_list(self):
        response = self.client.get(f'{self.base_url}/')
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_create(self):
        data = {
            "username": "user3"
        }
        response = self.client.post(f'{self.base_url}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_id = response.data['id']
        new_user = User.objects.get(id=user_id)
        new_user.refresh_from_db()
        self.assertEqual(User.objects.count(), 3)
        self.assertEqual(new_user.username, data['username'])

    def test_user_retrieve(self):
        url = f'{self.base_url}/{self.user1.pk}'
        response = self.client.get(url)
        serializer = UserSerializer(self.user1)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_user_update(self):
        url = f'{self.base_url}/{self.user1.pk}'
        data = {
            "username": "updated_user"
        }
        response = self.client.put(url, data, format='json')

        self.user1.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.user1.username, data['username'])

    def test_user_delete(self):
        url = f'{self.base_url}/{self.user1.pk}'
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 1)
