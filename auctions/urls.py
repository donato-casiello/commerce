from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_auction", views.create, name="create"),
    path("<int:auction_id>", views.detail, name="detail"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("category", views.category, name="category")
]
