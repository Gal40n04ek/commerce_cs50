from django.contrib import admin
from django.urls import path, re_path
from django.conf.urls.static import static
from django.conf.urls import handler404
from django.conf.urls import include, url

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add", views.addListing, name="add"),
    path("<int:listing_id>", views.listing_view, name="listing"),
    path("<int:listing_id>/comment", views.comment, name="comment"),
    path("<int:listing_id>/makeBid", views.makeBid, name="makeBid"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("<int:listing_id>/changewatchlist", views.changeWatchList, name="changeWatchList"),
    path("<int:listing_id>/close", views.closeListing, name="closeListing"),
    path("activelistings", views.activelistings, name="activelistings"),
    re_path(r'^activelistings&(?:category=(?P<category_id>\d+)/)/?$', views.activelistings, name="activelistings"),
    path("categories", views.categories, name="categories"),
]

# handler404 = 'auctions.views.error404'