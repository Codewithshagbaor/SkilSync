
from typing import ClassVar

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractUser):
    """Default user for Skillsync"""
    
    name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(_("email address"), unique=True)
    
    username = None  # type: ignore[assignment]
    
    avatar = models.URLField(max_length=200, null=True, blank=True)
    wallet_address = models.CharField(max_length=42, unique=True, null=True)
    nonce = models.CharField(max_length=100, null=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    # def __str__(self):
    #     return self.name



