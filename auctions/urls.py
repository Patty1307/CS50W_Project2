from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("CreateListing", views.CreateListing_view, name="CreateListing"),
    path("categories", views.categories_view, name="categories"),
    path("categories/<int:category_id>", views.category, name="category"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("listing/<int:listing_id>/bid", views.place_bid, name="place_bid"),
    path("listing/<int:listing_id>/comment", views.comment, name="comment"),
    path("listing/<int:listing_id>/close", views.close_auction, name="close_auction"),
    path("listing/<int:listing_id>/watch", views.toggle_watchlist, name="toggle_watchlist"),
    path("profile/<int:user_id>", views.profile, name="profile"),
    path("register", views.register, name="register"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("won_auctions", views.won_auctions, name="won_auctions")
]
