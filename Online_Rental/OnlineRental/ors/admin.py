from django.contrib import admin

# Register your models here.
from .models import *

admin.site.register([UserProfile,
						LoginTrail,
						Wishlist,
						Product,
						RequestSeller,
						ProductRating,
						SellerRating,
						Report,
						OrderHistory,
						ArchivedProduct,
						ProductImage,
						])