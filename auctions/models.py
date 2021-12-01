from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

from django.db.models.deletion import CASCADE, PROTECT

from commerce.settings import BASE_DIR
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime
from django.utils import timezone

class User(AbstractUser):
    pass

class Category(models.Model):
    category = models.CharField(max_length=64)

    def __str__(self):
        return self.category

class Listing(models.Model):
    title = models.CharField(max_length=60)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="similarItems")
    description = models.CharField(max_length=256)
    cost = models.IntegerField()
    offerBid = models.IntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='media', default='no_image.jpg', blank=True, null=True)
    timeCreated = models.DateTimeField(default=timezone.now, blank=True)
    activeFlag = models.BooleanField(default=True)
    seller = models.ForeignKey(User, blank=True, on_delete=models.PROTECT, related_name="allSellersItems")
    winner = models.ForeignKey(User, null=True, on_delete=models.PROTECT)
    watchings = models.ManyToManyField(User, blank=True, related_name="watchedListings")

    def __str__(self):
        return self.title

class Comment(models.Model):
    commentContent = models.CharField(max_length=256)
    listingItem = models.ManyToManyField(Listing, related_name="allComments")
    timeAdded = models.DateTimeField(default=timezone.now, blank=True)
    user = models.CharField(max_length=60)
    
    def __str_(self):
        return self.commentContent

class Bid (models.Model):
    auction = models.ForeignKey(Listing, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    offer = models.IntegerField()
    offerTime = models.DateTimeField(default=timezone.now, blank=True)
