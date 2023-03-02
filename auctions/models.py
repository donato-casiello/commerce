from django.db import models
from django.contrib.auth.models import AbstractUser


# An Abstract User is a class of user that can be easily change if the need
class User(AbstractUser):
    pass
