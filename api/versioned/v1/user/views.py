from rest_framework import viewsets, permissions, status, mixins
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from api.bases.user.models import User
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




class UserViewSet(MappingViewSetMixin,
                     viewsets.ModelViewSet):

    permission_classes = [AllowAny, ]
    queryset = User.objects.all()
    serializer_class = UserSerializer
