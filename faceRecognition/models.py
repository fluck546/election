from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager,
)
from django.db import models
import json


class CustomUserManager(BaseUserManager):
    def create_user(self, sid, password=None, **extra_fields):
        if not sid:
            raise ValueError("The Sid field must be set")
        user = self.model(sid=sid, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, sid, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(sid, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    sid = models.CharField(max_length=20, unique=True)
    face_encoding = models.TextField(
        blank=True, null=True, unique=True
    )  # Store face encoding as text
    name = models.CharField(max_length=40, blank=True, null=True)
    last_name = models.CharField(max_length=40, blank=True, null=True)
    branch = models.CharField(max_length=40, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email = models.EmailField(max_length=50, blank=True,null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "sid"
    REQUIRED_FIELDS = ['name']

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",  
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_permissions_set",  # Avoid conflict with auth.User
        blank=True,
    )

    def __str__(self):
        return self.sid

    def set_face_encoding(self, encoding):
        """Store face encoding as JSON string."""
        self.face_encoding = json.dumps(encoding)

    def get_face_encoding(self):
        """Retrieve face encoding as a Python list."""
        if self.face_encoding:
            return json.loads(self.face_encoding)
        return None
