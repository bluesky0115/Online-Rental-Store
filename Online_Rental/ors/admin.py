from django.contrib import admin

from .models import *

admin.site.register([UserProfile,
						LoginTrail,
						Product,
						RequestSeller,
						Wishlist,
						ProductRating,
						SellerRating,
						Report,
						OrderHistory,
						ArchivedProduct,
						])
