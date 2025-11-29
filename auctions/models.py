from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

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
