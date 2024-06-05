from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('accountant', 'Accountant'),
        ('manager', 'Manager'),
    )

    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='manager')

    def __str__(self):
        return self.email
