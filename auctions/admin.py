from django.contrib import admin

# Register your models here.
from .models import Listing, Comment, Category, Bid, User

admin.site.register(Listing)
admin.site.register(Comment)
admin.site.register(Category)
admin.site.register(Bid)
admin.site.register(User)