from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from decimal import Decimal

from .models import User, Auction, Bid, Comment


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
        bid_decimal = Decimal(bid)
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
    # Get the auction data
    auction = Auction.objects.get(pk=auction_id)
    user = User.objects.get(id=request.user.id)
    bids = Bid.objects.filter(auction_id=auction.id)
    if not bids:
        price = auction.start_bid
    else:
        price = max(bid.amount for bid in bids )
    # User submit the form
    if request.method == "POST":
        # The user created the auction
        if auction.owner.id == request.user.id:
            if 'close' in request.POST:
                auction.active = False
                auction.save()
                # There was some bids
                if price != auction.start_bid:
                    highest_bid = Bid.objects.filter(auction_id=auction.id, amount=price).first()
                    messages.success(request, f"Auction has been closed. The winner is {highest_bid.user_id}")
                else:
                    messages.success(request, "Auction has been closed. Nobody put a bid on this item")
                return HttpResponseRedirect(reverse('detail', args=[auction.id]))
        # User doesn't create the auction
        else:
            # Check for comments
            if 'comment' in request.POST and request.POST["comment"].strip() != "":
                comment = Comment.objects.create(auction_id=auction, comment=request.POST["comment"], user_id=request.user)
                comment.save()
            # Check for bid
            elif 'amount' in request.POST:
                amount = float(request.POST["amount"])
                if amount > price:
                    new_bid = Bid.objects.create(auction_id=auction, amount=amount, user_id=user)
                else:
                    message = "Your bid must be greater"
                    return render(request, "auctions/detail.html", {
                        "auction" : auction,
                        "price" : price,
                        "start_bid" : auction.start_bid, 
                        "message" : message, 
                    })
            return HttpResponseRedirect(reverse('detail', args=[auction.id]))
    else:
        comments = Comment.objects.filter(auction_id=auction)
        return render(request, "auctions/detail.html", {
            "auction" : auction,
            "price" : price,
            "start_bid" : auction.start_bid,
            "owner" : auction.owner,
            "user_id" : user.id,
            "comments" : comments
        })
        
    
