from django.db.models import Max
from rest_framework import viewsets, permissions, status, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.bases.chat.models import ChatRoomParticipant
from api.bases.user.models import User
from api.versioned.v1.user.serializers import UserSerializer
from common.viewsets import MappingViewSetMixin

import arrow

class BaseViewSet(MappingViewSetMixin,
                      viewsets.GenericViewSet,
                      ):
    permission_classes = [permissions.AllowAny]
    # filter_backends = (filters.DjangoFilterBackend,)
    filter_class = None
    serializer_class = None

    def get_queryset(self):
        return None




class UserViewSet(MappingViewSetMixin,
                     viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActiveUsersView(MappingViewSetMixin, viewsets.GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = UserSerializer

    def get_user_active(self, request, *args, **kwargs):
        thirty_minutes_ago = arrow.now("Asia/Seoul").shift(minutes=-30).datetime
        active_users = User.objects.filter(last_active__gte=thirty_minutes_ago)
        serializer = self.get_serializer(active_users, many=True)
        return Response(serializer.data)