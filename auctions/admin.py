from django.contrib import admin

from .models import Listing, Category, Watchlist, Bid
# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id","created", "owner", "title","starting_bid", "category", "active","bids_count","highest_bid_user","edited")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing")

admin.site.register(Listing,ListingAdmin)
admin.site.register(Category)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid)