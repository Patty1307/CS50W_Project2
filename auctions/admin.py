from django.contrib import admin

from .models import Listing, Category
# Register your models here.
class ListAdmin(admin.ModelAdmin):
    list_display = ("id","created", "owner", "title","starting_bid", "category", "active","edited")

admin.site.register(Listing,ListAdmin)
admin.site.register(Category)