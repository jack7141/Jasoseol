from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.bases.chat.models import ChatRoom, ChatRoomParticipant
from api.bases.user.models import User
from api.versioned.v1.chat.serializers import ChatRoomSerializer, ChatRoomParticipantSerializer
from api.versioned.v1.user.serializers import UserSerializer
from common.viewsets import MappingViewSetMixin


class BaseViewSet(MappingViewSetMixin,
                      viewsets.GenericViewSet,
                      ):
    permission_classes = [permissions.AllowAny]
    # filter_backends = (filters.DjangoFilterBackend,)
    filter_class = None
    serializer_class = None

    def get_queryset(self):
        return None



class ChatRoomViewSet(MappingViewSetMixin,
                     viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = ChatRoom.objects.all()
    serializer_class = ChatRoomSerializer




class ChatRoomParticipantViewSet(MappingViewSetMixin,
                                    viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = ChatRoomParticipant.objects.all()
    serializer_class = ChatRoomParticipantSerializer

    def filter_queryset(self, queryset):
        queryset = queryset.filter(**self.kwargs)
        queryset = super().filter_queryset(queryset=queryset)
        return queryset

    def get_participants(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        users = User.objects.filter(id__in=queryset.values_list('user_id', flat=True))
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)