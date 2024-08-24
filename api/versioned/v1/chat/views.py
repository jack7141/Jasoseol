from rest_framework import viewsets, permissions
from rest_framework.permissions import AllowAny

from api.bases.chat.models import ChatRoom
from api.versioned.v1.chat.serializers import ChatRoomSerializer
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

