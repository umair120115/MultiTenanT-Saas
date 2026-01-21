import uuid
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.utils import timezone
from decimal import Decimal

class AppUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError("Username is required!")
        if not password:
            raise ValueError("Password is required!")

        extra_fields.setdefault("is_active", True)
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)

        return self.create_user(username, password, **extra_fields)


class Users(AbstractBaseUser):
    ROLES = (
        ('admin','Admin'),
        ('employee','Employee'),
        ('manager','Manager')
    )
    GENDER = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('undisclose', 'Undisclose')
    )
    MARITALSTATUS=(
        ('single', 'Single'),
        ('married', 'Married'),
        ('undisclose','Undisclose')
    )

    id=models.UUIDField(primary_key=True, default=uuid.uuid4, editable =False)
    username = models.CharField( max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, choices=ROLES, default='employee')
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=255, blank=True, null=True)
    profileImage = models.ImageField(upload_to='profile/',blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=255, choices=GENDER, default='undisclose' )
    maritalStatus = models.CharField(max_length=255, choices=MARITALSTATUS, default='Undisclose')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_phoneverified= models.BooleanField(default=False)
    is_emailverified = models.BooleanField(default=False)
    profileCompleted = models.BooleanField(default=False)
    is_hotel_owner =models.BooleanField(default=False)
    is_restuarant_owner = models.BooleanField(default=False)
    is_both = models.BooleanField(default=False)
    fcm_token = models.CharField(max_length=255, blank=True, null=True)
    latitude = models.CharField(max_length=255, blank=True, null=True)
    longitude = models.CharField(max_length=255, blank=True, null=True)
    platform = models.CharField(max_length=255, blank=True, null=True)
    expo_token = models.CharField(max_length=255, blank=True, null=True)
    date_joined = models.DateField(auto_now_add=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name", "password", "username"]

    objects = AppUserManager()

    def __str__(self):
        return self.name or self.phone or self.email

    def has_module_perms(self, app_label):
        return True

    def has_perm(self, perm, obj=None):
        return True
