from django.db import models
from django.contrib.auth.models import AbstractUser


# An Abstract User is a class of user that can be easily change if the need
class User(AbstractUser):
    pass

class Auction(models.Model):
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=200)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    start_bid = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    active = models.BooleanField(default=True)
    image = models.ImageField(upload_to='auctions_images/', blank=True)
    category = models.CharField(max_length=64, blank=True)
    def __str__(self):
        return f"{self.title} : {self.owner}"
    
class Bid(models.Model):
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
class Comment(models.Model):
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    comment = models.TextField(max_length=200)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.user_id} made a comment for {self.auction_id}"

class Watchlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    auction_id = models.ForeignKey(Auction, on_delete=models.CASCADE)
    watchlist = models.BooleanField(default=False)