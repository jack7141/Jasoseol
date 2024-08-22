from rest_framework import serializers

from api.bases.chat.models import ChatRoom


class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = '__all__'
