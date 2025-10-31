"""
Custom User model for NileFi with Hedera wallet integration.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserRole(models.TextChoices):
    """User role choices"""
    STARTUP = 'STARTUP', 'Startup'
    LENDER = 'LENDER', 'Lender'
    ADMIN = 'ADMIN', 'Admin'


class UserManager(BaseUserManager):
    """Custom user manager for Hedera-based authentication"""
    
    def create_user(self, hedera_account_id, role=UserRole.STARTUP, **extra_fields):
        """Create and save a regular user"""
        if not hedera_account_id:
            raise ValueError('Hedera Account ID must be provided')
        
        user = self.model(
            hedera_account_id=hedera_account_id,
            role=role,
            **extra_fields
        )
        user.save(using=self._db)
        return user
    
    def create_superuser(self, hedera_account_id, **extra_fields):
        """Create and save a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', UserRole.ADMIN)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(hedera_account_id, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User model using Hedera account ID as primary identifier.
    No passwords - authentication via wallet signature verification.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hedera_account_id = models.CharField(max_length=50, unique=True, db_index=True)
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.STARTUP)
    
    # Profile information
    name = models.CharField(max_length=200, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    profile_meta = models.JSONField(default=dict, blank=True)
    
    # Django admin permissions
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'hedera_account_id'
    REQUIRED_FIELDS = []
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.hedera_account_id} ({self.get_role_display()})"
    
    def get_full_name(self):
        return self.name or self.hedera_account_id
    
    def get_short_name(self):
        return self.name or self.hedera_account_id[:10]


class AuthNonce(models.Model):
    """
    Temporary nonces for wallet signature authentication.
    Nonces expire after 5 minutes for security.
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hedera_account_id = models.CharField(max_length=50, db_index=True)
    nonce = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'auth_nonces'
        verbose_name = 'Auth Nonce'
        verbose_name_plural = 'Auth Nonces'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['hedera_account_id', 'nonce']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"Nonce for {self.hedera_account_id}"
    
    def is_valid(self):
        """Check if nonce is still valid"""
        return not self.used and timezone.now() < self.expires_at
    
    def mark_used(self):
        """Mark nonce as used"""
        self.used = True
        self.save(update_fields=['used'])
