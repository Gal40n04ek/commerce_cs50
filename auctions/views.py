from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.forms.models import ModelForm
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.core.files import File 
import os
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.decorators import login_required

from django.template import Context, loader

from .models import User, Listing, Comment, Category, Bid
from django import forms

# class NewListingForm(forms.Form):
#     title = forms.CharField(label="Item Title", widget = forms.TextInput(attrs={"class":"form-control col-md-6 col-lg-4"}))
#     category = forms.ChoiceField(label="Category", choices=[] widget = forms.Select(attrs={"class": "form-control col-md-4 col-lg-2"}))
#     description = forms.CharField(label="Description", widget = forms.Textarea(attrs={"class": "form-control col-md-8 col-lg-6", "rows": 5}))
#     cost = forms.IntegerField(label="Start cost in $", widget = forms.NumberInput)
#     image = forms.ImageField(label="Listing Image", widget = forms.FileInput, required=False)

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields =['title', 'category', 'description', 'cost', 'image']
        widgets = {
            'title': forms.TextInput(attrs={"class":"form-control col-md-6 col-lg-4"}),
            'category': forms.Select(attrs={"class": "form-control col-md-4 col-lg-2"}),
            'description': forms.Textarea(attrs={"class": "form-control col-md-8 col-lg-6", "rows": 5}),
            'cost': forms.NumberInput,
            'image': forms.FileInput
        }
    
class NewCommentForm(forms.Form):
    author = forms.CharField(label="Username", widget = forms.TextInput(attrs={"class":"form-control col-md-6 col-lg-4"}))
    commentContent = forms.CharField(label="Leave a comment", widget = forms.Textarea(attrs={"class": "form-control col-md-8 col-lg-6", "rows": 5}))

class NewBidForm(forms.Form):
    offer = forms.IntegerField(label="Offer in $", widget = forms.NumberInput(attrs={'style': 'width: 70px'}))


def index(request):
    return render(request, "auctions/index.html", {
        "listings": Listing.objects.all(),
        "categories": Category.objects.all()
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
                "message": "Username is already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

@login_required
def addListing (request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            title = form.cleaned_data["title"]
            description = form.cleaned_data["description"]
            category = form.cleaned_data ["category"]
            cost = form.cleaned_data["cost"]
            #image = form.cleaned_data["image"]
            seller = request.user
            if request.FILES is not None:
                image = request.FILES.get('image')
            if image is not None:
                newListing = Listing(title=title, category = category, description=description, cost=cost, image=image, seller=seller)
            else:
                newListing = Listing(title=title, category = category, description=description, cost=cost, seller=seller)
            newListing.save()

            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/add.html", {
                "form": form
            })
    return render (request, "auctions/add.html", {
        "form": NewListingForm()
    })

def listing_view(request, listing_id):
    
    try:
        listing = Listing.objects.get(id=listing_id)
    except:
        return render(request, "404.html")
    if request.user == listing.seller and listing.activeFlag:
        closeMessage = True
    else:
        closeMessage = False
    comments = listing.allComments.all()
    if request.user in listing.watchings.all():            
        checker = False
    else:
        checker = True
    return render(request, "auctions/listing.html", {
        "listing": listing,
        "comments": comments,
        "bidForm": NewBidForm(),
        "form": NewCommentForm(),
        "closeMessage": closeMessage,
        "checker": checker,
    })
    
    

@login_required
def comment(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(pk=listing_id)
        form = NewCommentForm(request.POST)
        comments = listing.allComments.all()
        if form.is_valid:
            commentText = request.POST["commentContent"]
            author = request.POST["author"]
            newComment = Comment(commentContent=commentText, user=author)
            newComment.save()
            newComment.listingItem.set([listing_id])
            comments = listing.allComments.all()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
        
    return render(request, "auctions/listing.html", {
            "listing": listing,
            "comments": comments,
            "form": NewCommentForm(),
            "bidForm": NewBidForm(),            
        })

@login_required
def makeBid(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id = listing_id)
        offer = int(request.POST['offer'])
        form = NewBidForm(request.POST)
        if form.is_valid:
            #check whether offer is valid
            if offer >= listing.cost and (listing.offerBid is None or offer > listing.offerBid):
                listing.offerBid = offer
                newBid = Bid(auction = listing, buyer = request.user, offer = offer)
                newBid.save()
                listing.save() 
                success = True             
                # return HttpResponseRedirect(reverse("listing", args=(listing_id)))
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidForm": NewBidForm(),
                    "comments": listing.allComments.all(),
                    "success": True,                    
                    "form": NewCommentForm(),
                })
            else:
                if offer < listing.cost:
                    lastCost = listing.cost
                else:
                    lastCost = listing.offerBid
                return render(request, "auctions/listing.html", {
                    "listing": listing,
                    "bidForm": NewBidForm(),
                    "comments": listing.allComments.all(),
                    "error": True,
                    "lastCost": lastCost,
                    "form": NewCommentForm(),
                })
    return render(request, "auctions/listing.html", {
                "listing": listing,
                "bidForm": NewBidForm(),
                "comments": listing.allComments.all(),
                "form": NewCommentForm(),
            })

@login_required
def watchlist(request):
    listings = Listing.objects.filter(watchings = request.user)
    categories = Category.objects.all()
    return render(request, "auctions/watchlist.html", {
        "listings": listings,
        "categories": categories,
    })


def activelistings(request, category_id=None):
    if category_id is None:
        listings = Listing.objects.filter(activeFlag = True)
    else:
        listings = Listing.objects.filter(activeFlag = True, category = category_id)
    categories = Category.objects.all()
    return render(request, "auctions/activelistings.html", {
        "listings": listings,     
        "categories": categories,
    })

def closeListing(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id = listing_id)
        if request.user == listing.seller:
            listing.activeFlag = False
            listing.winner = Bid.objects.filter(auction = listing).last().buyer
            listing.save()
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

@login_required
def changeWatchList(request, listing_id):
    if request.method == "POST":
        listing = Listing.objects.get(id = listing_id)
        if request.user in listing.watchings.all():
            listing.watchings.remove(request.user)
        else:
            listing.watchings.add(request.user)
    return HttpResponseRedirect(reverse("listing", args=(listing_id,)))


def categories(request):
    categories = Category.objects.all()
    listings = Listing.objects.all()
    # listings = Listing.objects.filter(category = category_id)
    return render(request, "auctions/categories.html", {
        "categories": categories,
        "listings": listings,
    })

# def error404(request, exception):
#     return render(request, 'auctions/404.html', status=404)

