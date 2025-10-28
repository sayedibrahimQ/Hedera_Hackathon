
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user model for NileFi."""

    hedera_account_id = models.CharField(max_length=255, blank=True, null=True)
    # Add other user-related fields here
