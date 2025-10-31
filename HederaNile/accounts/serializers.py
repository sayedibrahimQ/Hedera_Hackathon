"""
Django REST Framework serializers for accounts app.
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AuthNonce
import json


User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration via wallet."""
    
    class Meta:
        model = User
        fields = ['hedera_account_id', 'name', 'email', 'role', 'profile_meta']
        extra_kwargs = {
            'hedera_account_id': {'required': True},
            'name': {'required': True},
            'email': {'required': True},
            'role': {'required': True}
        }
    
    def validate_hedera_account_id(self, value):
        """Validate Hedera account ID format."""
        if not value.startswith('0.0.'):
            raise serializers.ValidationError("Invalid Hedera account ID format")
        return value
    
    def validate_profile_meta(self, value):
        """Validate profile_meta is valid JSON."""
        if value and not isinstance(value, dict):
            raise serializers.ValidationError("profile_meta must be a valid JSON object")
        return value


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile display and updates."""
    
    class Meta:
        model = User
        fields = ['id', 'hedera_account_id', 'name', 'email', 'role', 
                 'profile_meta', 'date_joined', 'last_login']
        read_only_fields = ['id', 'hedera_account_id', 'date_joined', 'last_login']


class UserPublicSerializer(serializers.ModelSerializer):
    """Serializer for public user information (used in funding displays)."""
    
    class Meta:
        model = User
        fields = ['id', 'name', 'role', 'date_joined']


class AuthNonceSerializer(serializers.ModelSerializer):
    """Serializer for authentication nonce generation."""
    
    class Meta:
        model = AuthNonce
        fields = ['hedera_account_id', 'nonce']
        read_only_fields = ['nonce']


class WalletAuthSerializer(serializers.Serializer):
    """Serializer for wallet signature authentication."""
    hedera_account_id = serializers.CharField(max_length=50)
    signature = serializers.CharField()
    nonce = serializers.CharField()
    
    def validate_hedera_account_id(self, value):
        """Validate Hedera account ID format."""
        if not value.startswith('0.0.'):
            raise serializers.ValidationError("Invalid Hedera account ID format")
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer for password reset requests (wallet-based)."""
    hedera_account_id = serializers.CharField(max_length=50)
    new_signature = serializers.CharField()
    nonce = serializers.CharField()


class RoleUpdateSerializer(serializers.Serializer):
    """Serializer for admin role updates."""
    user_id = serializers.UUIDField()
    new_role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    reason = serializers.CharField(max_length=500, required=False)


class UserStatsSerializer(serializers.Serializer):
    """Serializer for user statistics (admin dashboard)."""
    total_users = serializers.IntegerField()
    startups = serializers.IntegerField()
    lenders = serializers.IntegerField()
    admins = serializers.IntegerField()
    new_users_today = serializers.IntegerField()
    new_users_week = serializers.IntegerField()
    active_users_week = serializers.IntegerField()