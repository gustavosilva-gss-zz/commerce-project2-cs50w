from django.contrib import admin
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from .models import User, Listing, Bid, Category, Comment, Watchlist

admin.site.register(User)
admin.site.register(Bid)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Watchlist)

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "image_url", "min_bid")
    readonly_fields = ("bids", "comments")

    def bids(self, obj):
        #show a table with the listing's bids
        bids_list = list(obj.bids.all())

        if not bids_list:
            return mark_safe("<span class='errors'>No bids</span>")

        return render_to_string('auctions/admin/bids_table_admin.html', {'bids':bids_list})
    
    def comments(self, obj):
        #show a table with the listing's comments
        comments = list(obj.comments.all())

        if not comments:
            return mark_safe("<span class='errors'>No comments</span>")

        return render_to_string('auctions/admin/comments_table_admin.html', {'comments':comments})

admin.site.register(Listing, ListingAdmin)