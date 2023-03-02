from django.contrib import admin

from .models import User, Auction, Bid, Comment

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = "id", "username"

class AuctionAdmin(admin.ModelAdmin):
    list_display = "title", "owner", "active"
    
admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Bid)
admin.site.register(Comment)