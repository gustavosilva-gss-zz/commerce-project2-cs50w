from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator

class User(AbstractUser):
    pass

class Category(models.Model):
    #made it as a model, so the admins can add/remove categories
    class Meta:
        verbose_name_plural = "categories" #fix the plural in admin

    title = models.CharField(max_length=30)

    def __str__(self):
        return self.title

class Listing(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=1000, validators=[MaxLengthValidator(1000)])
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="listings")
    min_bid = models.DecimalField(max_digits=11, decimal_places=2) #allow up to 999.999.999,99
    image_url = models.URLField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="listings")
    active = models.BooleanField(default=True) #see if listing is closed or still active

    def __str__(self):
        return self.title

class Bid(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    value = models.DecimalField(max_digits=11, decimal_places=2)

    def __str__(self):
        return f"{self.user} - {self.listing}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField(max_length=500, validators=[MaxLengthValidator(1000)])

    def __str__(self):
        return f"{self.user} - {self.content}"

class Watchlist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    listings = models.ManyToManyField(Listing, related_name="watchlist")

    def __str__(self):
        return f"{self.user}'s watchlist"