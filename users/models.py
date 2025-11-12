from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    is_barber = models.BooleanField(default=False)
    is_client = models.BooleanField(default=True)
    phone = models.CharField(max_length=15, blank=True, null=True)