from django.contrib import admin

from .models import User, Auction

# Register your models here.
"""class UserAdmin(admin.ModelAdmin):
    list_display = "id", "username" """
    
admin.site.register(User)
admin.site.register(Auction)
