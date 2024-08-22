from common.routers import CustomSimpleRouter
from .views import ChatRoomViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register(r'', ChatRoomViewSet)

urlpatterns = [
]

urlpatterns += router.urls