from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, models
from django.db.models import Exists, OuterRef, Value, BooleanField, Subquery
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django import forms

from .models import User, Listing, Watchlist, Bid, Category

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

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ["bid"]
        labels = {"bid": ""}
        widgets = {
            "bid": forms.NumberInput(attrs={"class": "form-control", "placeholder": "Place your bid", "min":"0"})
        }
   

def index(request):
 
    listings = get_active_listings_with_watchflag(request.user)
     
    return render(request, "auctions/index.html",{
        "Listings": listings,
        "header" : "Active Listings"
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
    # the get_object_or_404 ist a good shortcut for the possibility there is no objects. Faster then 'try'
    listing = get_object_or_404(Listing, id=listing_id)
    
    is_watching = False
    form = None
    if request.user.is_authenticated:
        is_watching = Watchlist.objects.filter(
            user=request.user,
            listing=listing
        ).exists()
            
        form = BidForm()

    return render(request, "auctions/listing.html",{
        "listing" : listing,
        "is_watching" : is_watching,
        "form_bid" : form,
        "user_has_highest": listing.user_has_highest_bid(request.user)
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

@login_required 
def toggle_watchlist(request, listing_id):
    if request.method == "POST":
         # Get the Listing Objects we wanna watch oder delete the watch
         listing = get_object_or_404(Listing, pk=listing_id)
         # get_or_create gives back a tuple you can unapck with two variables
         # Watch_entry = The Database Entry/obejct
         # created = True or False
         watch_entry, created = Watchlist.objects.get_or_create(
             user = request.user,
             listing = listing
         )
        # When no new Databaseentry ist created then delete the old one
         if not created:
             watch_entry.delete()
    
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

@login_required 
def place_bid(request,listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    
    if request.method == "POST":
        form = BidForm(request.POST)
        form.instance.listing = listing
        form.instance.user = request.user

        if form.is_valid():
            form.save()
            messages.success(request, "Your bid was placed successfully.")
        else:
            for errors in form.errors.values():
                for error in errors:
                    messages.add_message(request, messages.ERROR, error, extra_tags="danger")
            
    return HttpResponseRedirect(reverse('listing', args=[listing_id]))

def profile(request,user_id):
    user = get_object_or_404(User, pk=user_id)

    return render(request, "auctions/profile.html",{
        "user" : user
    })

@login_required
def close_auction(reqeust, listing_id):
    if reqeust.method == "POST":
        listing = get_object_or_404(Listing, pk=listing_id)
        listing.active = False
        listing.save()
    return redirect("index")

@login_required
def watchlist(request):
    listings = get_active_listings_with_watchflag(request.user).filter(
        watchlisted_by__user=request.user
    )

    return render(request, "auctions/index.html", {
        "Listings": listings,
        "header" : "Watchlist"
    })

def categories_view(request):
    categories = Category.objects.all().order_by("name")
    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, category_id):

    category = get_object_or_404(Category, pk=category_id)
    listings = get_active_listings_with_watchflag(request.user).filter(category = category)
    
    return render(request, "auctions/index.html", {
        "header": f"Category: {category}",
        "Listings": listings
    })

@login_required
def won_auctions(request):
    listings = get_won_auctions_for_user(request.user)

    return render(request, "auctions/index.html", {
        "header": "Won auctions",
        "Listings": listings
    })


def get_active_listings_with_watchflag(user):

    #Gives back a List with every actice Listing and annotation to Watchlist if logged in
    qs = Listing.objects.filter(active=True)

    if user.is_authenticated:
        watch_qs = Watchlist.objects.filter(
            user = user,
            listing = OuterRef('pk')
        )

        qs = qs.annotate(
            is_on_watchlist=Exists(watch_qs)
        )
    else:
        qs = qs.annotate(
            is_on_watchlist=Value(False, output_field=BooleanField())
        )

    return qs.order_by("-created")

def get_won_auctions_for_user(user):
    highest_bid_qs = Bid.objects.filter(
        listing=OuterRef('pk')
    ).order_by('-bid')

    return (
        Listing.objects
        .filter(active=False)
        .annotate(
            winner_id=Subquery(highest_bid_qs.values('user_id')[:1])
        )
        .filter(winner_id__isnull=False, winner_id=user.id)
        .order_by('-created')
    )

