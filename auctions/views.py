from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from decimal import Decimal

from .models import User, Auction, Bid  


def index(request):
    auctions_list = Auction.objects.all()
    return render(request, "auctions/index.html", {
        "auctions_list" : auctions_list
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
    
@login_required(login_url='login')
def create(request):
    user = User.objects.get(id=request.user.id)
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        bid = request.POST["bid"]
        bid_decimal = float(bid)
        # Check the user's input
        if bid_decimal < 0 or bid_decimal> 1000000:
            message = "Starting bid must be a number greater than 0 and less than a 1.000.000"
            return render(request, "auctions/create.html", {
                "user" : user,
                "message" : message
            })
        new_auction = Auction(title=title, description=description, owner=user, start_bid=bid_decimal)
        new_auction.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "user" : user
        })

@login_required(login_url='login')
def detail(request, auction_id):
    auction = Auction.objects.get(pk=auction_id)
    id = Auction.objects.get(pk=auction_id)
    bids = Bid.objects.filter(auction_id=id)
    if not bids:
        price = auction.start_bid
    else:
        price = max(bid.amount for bid in bids )
    if request.method == "POST":
        amount = float(request.POST["amount"])
        if amount > price:
            user = User.objects.get(id=request.user.id)
            new_bid = Bid.objects.create(auction_id=id, amount=amount, user_id=user)
        else:
            message = "Your bid must be greater"
            return render(request, "auctions/detail.html", {
                "auction" : auction,
                "price" : price,
                "start_bid" : auction.start_bid, 
                "message" : message
            })
        return HttpResponseRedirect(reverse('detail', args=[auction.id]))
    else:
        return render(request, "auctions/detail.html", {
            "auction" : auction,
            "price" : price,
            "start_bid" : auction.start_bid
        })
        
    
