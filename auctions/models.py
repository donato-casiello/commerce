from django.db import models
from django.contrib.auth.models import AbstractUser


# An Abstract User is a class of user that can be easily change if the need
class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=50)
    bid = models.DecimalField(max_digits=6, decimal_places=2, default=0)
    
    def __str__(self):
        return f"{self.title} with bid: {self.bid} and id {self.id}"
