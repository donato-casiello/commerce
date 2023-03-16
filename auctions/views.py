from urllib.parse import urlencode
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.contrib import messages
from django.db.models import Max

from decimal import Decimal
from itertools import groupby
from datetime import date

from .models import User, Auction, Bid, Comment, Watchlist

CATEGORIES = ["Electronics", "Home appliances", "Home and garden", "Collecting and passions", "Fashion and beauty", "Mobility"]

def index(request):
    auctions_list = Auction.objects.filter(active=True)
    current_price = Bid.objects.values('auction_id').annotate(max_amount=Max('amount'))
    return render(request, "auctions/index.html", {
        "auctions_list" : auctions_list,
        "current_price" : current_price
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
            message = "Enter a valid bid: bid must be a number (for decimal numbers use dot '.' instead ',')"
            return render(request, "auctions/create.html", {
                "user" : user,
                "message" : message,
                "categories" : CATEGORIES
            })
        bid_decimal = Decimal(bid)
        # Check the user's input
        if bid_decimal < 0 or bid_decimal> 1000000:
            message = "Enter a valid bid: starting bid must be a number greater than 0 and less than a 1.000.000"
            return render(request, "auctions/create.html", {
                "user" : user,
                "message" : message,
                "categories" : CATEGORIES
            })
        # Check for images
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
        # The user created the auction, he can close the auction
        if auction.owner.id == request.user.id:
            if 'close' in request.POST:
                # There was some bids
                if price != auction.start_bid:
                    highest_bid = Bid.objects.filter(auction_id=auction.id, amount=price).first()
                    messages.success(request, f"Auction has been closed. The winner is {highest_bid.user_id}")
                    return HttpResponseRedirect(reverse('detail', args=[auction.id]))
                else:
                    messages.success(request, "Auction has been closed. Nobody put a bid on this item")
                auction.active = False
                auction.save()
                return HttpResponseRedirect(reverse('detail', args=[auction.id]))
        # User doesn't create the auction, he can bid, comment or add to watchlist
        else:
            # Check for comments
            if 'comment' in request.POST and request.POST["comment"].strip() != "":
                comment = Comment.objects.create(auction_id=auction, comment=request.POST["comment"], user_id=request.user)
                comment.save()
            # Check for bid
            elif 'amount' in request.POST:
                amount = float(request.POST["amount"])
                try:
                    amount_decimal = Decimal(amount)
                except:
                    messages.error(request, "Enter a valid bid: bid must be a number (for decimal numbers use dot '.' instead ',')")
                    return HttpResponseRedirect(reverse('detail', args=[auction.id]))
                amount_decimal = Decimal(amount)
                if amount_decimal > 10000 or amount_decimal < price:
                    messages.error(request, "You bid must be smaller than 10.000 and greater than the others")
                    return HttpResponseRedirect(reverse('detail', args=[auction.id]))
                else:
                    new_bid = Bid.objects.create(auction_id=auction, amount=amount, user_id=user)
                    new_bid.save()
                    return HttpResponseRedirect(reverse('detail', args=[auction.id]))
        # User add or remove auction from watchlist
        if 'add/remove' in request.POST:
            # Check the user already has the item inside his watchlist
            auction_id = request.POST["auction_id"]
            auction = Auction.objects.get(pk=auction_id)    
            watchlist_item = Watchlist.objects.filter(user_id=user, auction_id=auction).first()
            # If is the first time adding an auction, we have to create a new value inside the watchlist model
            if watchlist_item == None:
                new_watchlist = Watchlist(user_id=user, auction_id=auction, watchlist=True)
                new_watchlist.save()
                context = {"auction":auction, "price":price, "start_bid":auction.start_bid, "message_watchlist":"Add to watchlist"}
                return render (request, "auctions/detail.html", context)
            # The user want to remove the auction inside his watchlist
            elif watchlist_item.watchlist == True:
                watchlist_item.watchlist = False
                watchlist_item.save()
                context = {"auction":auction, "price":price, "start_bid":auction.start_bid, "message_watchlist":"Remove to watchlist"}
                return render (request, "auctions/detail.html", context)
            # The user want to add again 
            elif watchlist_item.watchlist == False:
                watchlist_item.watchlist = True
                watchlist_item.save()
                context = {"auction":auction, "price":price, "start_bid":auction.start_bid, "message_watchlist":"Add again to watchlist"}
                return render (request, "auctions/detail.html", context)
        if 'comment' in request.POST:
            return HttpResponseRedirect(reverse('detail', args=[auction.id]))
    # Render the detail page
    else:
        comments = Comment.objects.filter(auction_id=auction)
        message_watchlist = messages.get_messages(request)
        return render(request, "auctions/detail.html", {
            "auction" : auction,
            "price" : price,
            "start_bid" : auction.start_bid,
            "owner" : auction.owner,
            "user_id" : user.id,
            "comments" : comments,
        })


@login_required(login_url='login')
def watchlist(request):
    user = request.user
    watchlist_list = Watchlist.objects.filter(user_id=user, watchlist=True)
    return render (request, "auctions/watchlist.html", {
        "watchlist_list" : watchlist_list
    })

def category(request):
    """In this example, we're using the filter method to exclude auctions where the category is null, and the order_by method to sort the auctions by their category field.
    We're also using the groupby function to group the auctions by their category, 
    and storing the results in a dictionary with category names as keys and lists of auctions as values. 
    Finally, we're passing the categories dictionary to the template in a context dictionary."""
    auctions = Auction.objects.filter(active=True)
    categories = {}
    for auction in auctions:
        if auction.category:
            if auction.category not in categories:
                categories[auction.category] = []
            categories[auction.category].append(auction)
    return render(request, "auctions/category.html", {
        "categories": categories
    })

