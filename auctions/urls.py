from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("CreateListing", views.CreateListing_view, name="CreateListing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>/watch", views.toggle_watchlist, name="toggle_watchlist"),
    path("listing/<int:listing_id>/bid", views.place_bid, name="place_bid")
]
