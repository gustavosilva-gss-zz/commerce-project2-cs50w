from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import User, Listing, Comment, Bid, Watchlist, Category
from .forms import ListingForm


def index(request):
    #show only active listings
    listings = Listing.objects.filter(active=True)

    #create a list of dictionaries with the current bids
    current_bids = []
    for listing in listings:
        if listing.bids.exists():
            #get last bid (which is the most recent)
            bids = listing.bids.all().order_by("id").reverse() #order list, then reverse it
            value = bids[0].value
        else:
            #get minimum bid
            value = listing.min_bid

        current_bids.append({
            "value": value,
            "listing": listing.id
        })

        #format description to look better on the page
        listing.description = listing.description[:100]

    return render(request, "auctions/index.html", {
        "listings": listings,
        "current_bids": current_bids
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

@login_required
def new(request):
    if request.method == 'POST':
        post = request.POST.copy()
        post["user"] = User.objects.get(pk=request.user.id)

        form = ListingForm(post)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse("index"))

        return render(request, "auctions/new.html", {
            "form": form,
            "messages": form.errors.as_data
        })  
    
    listing_form = ListingForm()

    return render(request, "auctions/new.html", {
        "form": listing_form
    })

def listing(request, id):
    listing = Listing.objects.get(pk=id)

    watchlisted = False

    if request.user.is_authenticated:
        if hasattr(request.user, 'watchlist') and request.user.watchlist.listings.filter(pk=listing.id).exists():
            #this means that the user has a watchlist and it has this listing
            watchlisted = True

    current_bid = None #initialize
    if listing.bids.exists():
        #get last bid (which is the most recent)
        bids = listing.bids.all().order_by("id").reverse() #order list, then reverse it
        current_bid = bids[0].value

    if request.method == "POST":
        if not request.user.is_authenticated:
            messages.warning(request, 'Log in to submit comments, place bids and more!')
            return HttpResponseRedirect(reverse("listing", args=[listing.id]))

        else:
            if request.POST["type"] == "comment":
                #only calling makeing them outside this fuction to organize it all better
                submit_comment(request, listing, watchlisted)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

            elif request.POST["type"] == "bid":
                submit_bid(request, listing, current_bid)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

            elif request.POST["type"] == "close":
                close_listing(request, listing)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))
            
            elif request.POST["type"] == "watchlist":
                submit_watchlist(request, listing, watchlisted)
                return HttpResponseRedirect(reverse("listing", args=[listing.id]))

    if not listing.active:
        #it's possible the one who announced just closed it with no bids, thats why
        if listing.bids.exists():
            last_bid = listing.bids.all().order_by("id").reverse()[0]
            user_is_winner = request.user.id == last_bid.user.id
        else:
            user_is_winner = False

        return render(request, "auctions/listing.html", {
            "listing": listing,
            "current_bid": current_bid or listing.min_bid,
            "watchlisted": watchlisted,
            "user_is_winner": user_is_winner
        })

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "current_bid":current_bid or listing.min_bid,
        "watchlisted": watchlisted,
    })

def submit_comment(request, listing, watchlisted):
    #since people can change the html, I put some server-side verification
    if not request.POST["content"]:
        return render(request, "auctions/listing.html", {
            "listing": listing,
            "current_bid": current_bid or listing.min_bid,
            "watchlisted": watchlisted,
            "comment_error": "Content is required"
        })

    #it was easier to set the fields manually, thats why there's no ModelForm for comment
    comment = Comment(
        user = User.objects.get(pk=request.user.id),
        listing = listing,
        content = request.POST["content"]
    )

    comment.save()

def submit_bid(request, listing, current_bid):
    bid = Bid(
        user = User.objects.get(pk=request.user.id),
        listing = listing,
        value = float(request.POST["value"])
    )

    #cant be less than the minimum bid -> must be equal or greater than minimum bid
    #cant be less or equal to current_bid -> must be greater than minimum bid
    if bid.value < listing.min_bid:
        messages.warning(request, 'Your bid must be greater or equal to the current bid')
    if listing.bids.exists() and "{:.2f}".format(bid.value) <= "{:.2f}".format(current_bid):
        messages.warning(request, 'Your bid must be greater than the current bid')
    else:
        bid.save()

def close_listing(request, listing):
    listing.active = False
    listing.save()

def submit_watchlist(request, listing, watchlisted):
    if watchlisted:
        #then user wants to remove
        listings = request.user.watchlist.listings

        listings.remove(listing)
        print(listings.all())
    
    else:
        #means user wants to add
        if not hasattr(request.user, 'watchlist'):
            request.user.watchlist = Watchlist()
            watchlist = request.user.watchlist
            watchlist.save()

        listings = request.user.watchlist.listings

        listings.add(listing)

def watchlist(request):
    if hasattr(request.user, 'watchlist'):
        listings = request.user.watchlist.listings.all()

    else:
        listings = []

    return render(request, "auctions/watchlist.html", {
        "listings": listings
    }) 

def categories(request):
    categories = Category.objects.order_by('title')

    return render(request, "auctions/categories.html", {
        "categories": categories
    })

def category(request, id):
    category = Category.objects.get(pk=id)

    return render(request, "auctions/category.html", {
        "category": category
    })
