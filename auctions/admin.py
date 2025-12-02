from django.contrib import admin

from .models import Listing, Category, Watchlist, Bid, User, Comment
# Register your models here.
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id","created", "owner", "title","starting_bid", "category", "active","bids_count","highest_bid_user","edited")

class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "comment")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing", "bid")

admin.site.register(Listing,ListingAdmin)
admin.site.register(Category)
admin.site.register(Watchlist, WatchlistAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User)
admin.site.register(Comment, CommentAdmin)