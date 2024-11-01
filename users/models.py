from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    username = models.CharField(max_length=50,unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    subscribe = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class UserAddress(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    State = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    static_number = models.CharField(max_length=12)
    address = models.TextField()
