"""
Django admin configuration for accounts app.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, AuthNonce


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for User model"""
    
    list_display = ['hedera_account_id', 'name', 'email', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_staff', 'created_at']
    search_fields = ['hedera_account_id', 'name', 'email']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Hedera Wallet', {'fields': ('hedera_account_id',)}),
        ('Profile', {'fields': ('name', 'email', 'role', 'profile_meta')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at', 'last_login')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('hedera_account_id', 'name', 'email', 'role', 'is_active', 'is_staff'),
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at', 'last_login']


@admin.register(AuthNonce)
class AuthNonceAdmin(admin.ModelAdmin):
    """Admin interface for AuthNonce model"""
    
    list_display = ['hedera_account_id', 'nonce', 'used', 'created_at', 'expires_at']
    list_filter = ['used', 'created_at', 'expires_at']
    search_fields = ['hedera_account_id', 'nonce']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def has_add_permission(self, request):
        """Disable manual creation of nonces"""
        return False
