from django.contrib import admin

from .models import Auction, User

# Register your models here.

from .models import Auction, User

# Register your models here.

# This class is used to display a particular way in admin interface 
class AuctionAdmin(admin.ModelAdmin):
    list_display = "id", "title", "bid"

admin.site.register(Auction, AuctionAdmin)
admin.site.register(User)

