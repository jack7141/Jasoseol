from django.urls import path

from common.routers import CustomSimpleRouter
from .views import UserViewSet, BaseViewSet

router = CustomSimpleRouter(trailing_slash=False)
router.register(r'', UserViewSet)

urlpatterns = [
]

urlpatterns += router.urls