from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, Listing

class ListingForm(forms.ModelForm):
    # I am so glad that i found that in the django documentation.
    # This made the form so much easyier to connect it with the Model
    class Meta:
        model = Listing
        fields = ["title", "description", "starting_bid","image_url","category"]
        labels = {
            # Add * for required field. Didn't found an easy way to automate that....
            "title": "Titel*",
            "description": "Description*",
            "starting_bid": "Starting Bid*",
            "image_url": "Image URL",
            "category": "Category",
        }
        # Added some bootstrap for the style
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "starting_bid": forms.NumberInput(attrs={"class": "form-control"}),
            "image_url": forms.URLInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }

def index(request):
    listings = Listing.objects.filter(active=True).order_by("-created")
    return render(request, "auctions/index.html",{
        "Listings": listings
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def listing(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    return render(request, "auctions/listing.html",{
        "listing" : listing
    })

@login_required
def CreateListing_view(request):
    if request.method == "POST":
        form = ListingForm(request.POST)
        if form.is_valid():
            #The user/owner ist not in the submit. So save it but not commit it and add in the second stept the owner
            listing = form.save(commit=False)
            #Give the model the owner / current user
            listing.owner = request.user
            # Now save it
            listing.save()
            return HttpResponseRedirect(reverse("index"))
    else:
        form = ListingForm()
        return render(request, "auctions/CreateListing.html",{
            "form": form
        })