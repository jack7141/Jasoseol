from rest_framework import serializers

from api.bases.chat.models import ChatRoom, ChatRoomParticipant


class ChatRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoom
        fields = '__all__'



class ChatRoomParticipantSerializer(serializers.ModelSerializer):

    class Meta:
        model = ChatRoomParticipant
        fields = '__all__'