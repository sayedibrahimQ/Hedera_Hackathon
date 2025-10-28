
from rest_framework import serializers

from nilefi.apps.users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""

    class Meta:
        model = User
        fields = ("id", "username", "email", "hedera_account_id")
