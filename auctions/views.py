from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages

from decimal import Decimal
from itertools import groupby
from datetime import date

from .models import User, Auction, Bid, Comment, Watchlist

CATEGORIES = ["Electronics", "Home appliances", "Home and garden", "Engines", "Collecting and passions", "Fashion and beauty"]

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
        try:
            bid_decimal = Decimal(bid)
        except:
            message = "Enter a valid bid: bid must be a number"
            return render(request, "auctions/create.html", {
                "user" : user,
                "message" : message
            })
        bid_decimal = Decimal(bid)
        # Check the user's input
        if bid_decimal < 0 or bid_decimal> 1000000:
            message = "Enter a valid bid: starting bid must be a number greater than 0 and less than a 1.000.000"
            return render(request, "auctions/create.html", {
                "user" : user,
                "message" : message
            })
        if 'image' in request.FILES:
            image = request.FILES["image"]
        else:
            image = None
        if 'category' in request.POST:
            category = request.POST["category"]
        else:
            category = None
        now = date.today()
        new_auction = Auction(title=title, description=description, owner=user, start_bid=bid_decimal, image=image, category=category, date = now)
        new_auction.save()
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/create.html", {
            "user" : user, 
            "categories" : CATEGORIES 
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


@login_required(login_url='login')
def watchlist(request):
    user = request.user
    # If add/remove item to watchlist
    if 'add/remove' in request.POST:
        # Check the user already has the item inside his watchlist
        auction_id = request.POST["auction_id"]
        auction = Auction.objects.get(pk=auction_id)    
        watchlist_item = Watchlist.objects.filter(user_id=user, auction_id=auction).first()
        if watchlist_item:
            # The user already has the item in his watchlist
            watchlist_item.watchlist = False
            watchlist_item.save()
        else:
            # The user doesn't have the item in his watchlist
            new_watchlist_item = Watchlist(user_id=user, auction_id=auction, watchlist=True)
            new_watchlist_item.save()
        return render(request, "auctions/watchlist.html", {
            "user" : user,
            "message" : "Add to watchlist"
        })
    else:
        watchlist_item = Watchlist.objects.filter(user_id=user, watchlist=True)
        return render(request, "auctions/watchlist.html", {
            "watchlist_item" : watchlist_item
        })

def category(request):
    """In this example, we're using the filter method to exclude auctions where the category is null, and the order_by method to sort the auctions by their category field.
    We're also using the groupby function to group the auctions by their category, 
    and storing the results in a dictionary with category names as keys and lists of auctions as values. 
    Finally, we're passing the categories dictionary to the template in a context dictionary."""
    auctions = Auction.objects.all()
    categories = {}
    for auction in auctions:
        if auction.category:
            if auction.category not in categories:
                categories[auction.category] = []
            categories[auction.category].append(auction)
    return render(request, "auctions/category.html", {
        "categories": categories
    })

