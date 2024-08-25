from django.urls import path

from common.routers import CustomSimpleRouter
from .views import UserViewSet, ActiveUsersView

router = CustomSimpleRouter(trailing_slash=False)
router.register(r'', UserViewSet)

urlpatterns = [
    path(r'active', ActiveUsersView.as_view({'get': 'get_user_active'})),
]

urlpatterns += router.urls