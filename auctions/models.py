from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


class User(AbstractUser):
    pass

    @property
    def active_watchlist_count(self):
        return self.watchlist_items.filter(listing__active=True).count()

class Listing(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    category = models.ForeignKey('Category',on_delete=models.SET_NULL, blank=True, null=True)
    owner = models.ForeignKey('User', on_delete=models.CASCADE)
    active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title

# Each proberty is a column in this table. So Django handles everything with the joins etc. 
# Thats amazing. Its hard to unsterstand when you only knew SQL but makes live so much easier and better

    # 1) Give the object with the highest bid
    def highest_bid_obj(self):
        return self.bids.order_by("-bid").first()

    # 2) Gives the highest price from the listing back
    @property
    def highest_bid(self):
        highest = self.highest_bid_obj()
        return highest.bid if highest else self.starting_bid

    # 3) Count the bids
    @property
    def bids_count(self):
        return self.bids.count()

    # 4) Did the user has the higest bid
    def user_has_highest_bid(self, user):
        if not user.is_authenticated:
            return False

        highest = self.highest_bid_obj()
        if not highest:
            return False

        return highest.user == user
    
    @property
    def highest_bid_user(self):
        highest = self.highest_bid_obj()
        return highest.user if highest else None

class Watchlist(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name="watchlist_items")
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="watchlisted_by")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "listing") # One User can only be have the same Listing item once only in this Table/Model

    def __str__(self):
        return f"{self.user} → {self.listing}"

class Category(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class Bid(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="bids")
    bid = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateTimeField(auto_now_add=True)

    def clean(self):
        
        # Get highest bid
        highest_bid = Bid.objects.filter(listing=self.listing).order_by("-bid").first()

        # If there is already a bid, it must be higher.
        if highest_bid and self.bid <= highest_bid.bid:
            raise ValidationError(f"Bid must be higher then {highest_bid.bid} €")
        
        # In case there is no other bid, it must be higher then starting bid
        if not highest_bid and self.bid < self.listing.starting_bid:
            raise ValidationError(f"Bid must be a minimum of {self.listing.starting_bid} €")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

class Comment(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE)
    listing = models.ForeignKey('Listing', on_delete=models.CASCADE, related_name="comments")
    comment = models.CharField(max_length=1024)
    created = models.DateTimeField(auto_now_add=True)
    edited = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}: {self.comment[:30]}"