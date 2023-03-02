from django.db import models
from django.contrib.auth.models import AbstractUser


# An Abstract User is a class of user that can be easily change if the need
class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"'{self.title}' posted by {self.owner} is active: {self.active}"
    
class Bid(models.Model):
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)