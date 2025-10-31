from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError("The given username must be set")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    ROLE_INVESTOR = 'investor'
    ROLE_SME = 'sme'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_INVESTOR, 'Investor'),
        (ROLE_SME, 'SME'),
        (ROLE_ADMIN, 'Admin'),
    ]

    # re-declare username/email constraints if needed
    email = models.EmailField(_('email address'), unique=True, blank=False, null=False)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_SME)
    wallet_id = models.CharField(max_length=255, blank=True, null=True,
                                 help_text="Hedera account id (e.g., 0.0.xxxxx)")
    kyc_verified = models.BooleanField(default=False)
    # optional metadata you might want
    display_name = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f"{self.username} ({self.role})"
