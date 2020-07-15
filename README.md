# Commerce
### Submision for cs50w 2020 project 2

#### **Models**
All models are in the file `models.py`:
* Category - only superusers can create new
* Listing
* Bid
* Comment
* Watchlist

#### **Create Listing**
Users (who are logged in) can create a listing if they go to the path `/new`. There they'll find the requireds and optional fields.

#### **Active Listings**
The default path gives a page with all the active listings. Users can also access this page by the navigation bar.

#### **Listing Page**
This page is reached by going to `/listing/<listing_id>`, there the user will see all the details of the listing, as well as a few more things:
* User will see the current highest bid
* Clicking on the category of the lsiting will take the user to a page shwoing all listings for that category
* If the user is logged in, they'll be able to add/remove the listing from their watchlist
* There's a card with a field of value where the user can place their bid:
    * The bid must be greater than or the same as the minimum bid set by the one who created the listing
    * The user must be logged in to place a bid
* A button to close the listing will appear it's creator. This means the listing won't accept more bids and it won't appear in the "active listings" page.
* If the listing is closed, the user can see one out of two messages:
    * If they are the winner of the listing, the page will show a message saying they are the winner, as well as the value of their biding.
    * If they aren't the winner, there'll be a message saying the value of the winner's bid
* At the bottom, users can see all comments for the listings, as well as submiting one of their own

#### **Watchlist**
Users can see the listing they added to their watchlist by clicking in the "watchlist" button on the navigation bar (or go to route `/watchlist`). They can click on any of the page's listings, to see their respective listing.

#### **Categories**
TODO

#### **Django Admin Interface**
Going to `/admin`, the administrators can view, add, edit, and delete:
* Listings
* Comments
* Bids
* Categories
* Users
* Watchlists