from django import forms

from django.forms import ModelForm
from .models import Listing

# Create the form class.
class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'user', 'min_bid', 'image_url', 'category']