from django.urls import path
from common.routers import CustomSimpleRouter
from .views import ChatRoomViewSet, ChatRoomParticipantViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register(r'', ChatRoomViewSet)

urlpatterns = [
    path("<chat_room>/users", ChatRoomParticipantViewSet.as_view({'get': 'get_participants'})),
]

urlpatterns += router.urls