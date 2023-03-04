from django.contrib import admin

from .models import User, Auction, Bid, Comment

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = "id", "username"

class AuctionAdmin(admin.ModelAdmin):
    list_display = "id", "title", "owner", "start_bid", "active"
    
class BidAdmin(admin.ModelAdmin):
    list_display = "id", "auction_id", "amount", "user_id"
    
class CommentAdmin(admin.ModelAdmin):
    list_display = "id", "auction_id", "user_id"
    
admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Comment, CommentAdmin)