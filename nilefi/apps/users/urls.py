
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from nilefi.apps.users.views import UserViewSet

router = DefaultRouter()
router.register(r"users", UserViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
