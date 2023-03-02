from django.contrib import admin

from .models import Auction, User

# Register your models here.
class AuctionAdmin(admin.ModelAdmin):
    list_display = "id", "title", "bid"

admin.site.register(Auction, AuctionAdmin)
admin.site.register(User)
