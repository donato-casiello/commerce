from django.db import models
from django.contrib.auth.models import AbstractUser


# An Abstract User is a class of user that can be easily change if the need
class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"'{self.title}' posted by {self.owner}"