
from django.contrib import admin
from nilefi.apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for the User model."""

    list_display = ("username", "email", "hedera_account_id")
    search_fields = ("username", "email", "hedera_account_id")
