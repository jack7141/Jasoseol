from django.urls import path
from .views import StatusViewSet

urlpatterns = [
    path('', StatusViewSet.as_view({'get': 'status'}))
]
