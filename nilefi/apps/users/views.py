
from rest_framework import viewsets

from nilefi.apps.users.models import User
from nilefi.apps.users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for managing users."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
