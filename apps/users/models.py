from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # keep username, add unique email to allow email-based login
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email or self.username
