from django.urls import path,include
from django.contrib.auth import views as auth_views
#from django.contrib.auth import LogoutView
from django.views.generic.base import TemplateView
from . import views

app_name = 'ors'

urlpatterns = [
	path('', views.index, name='index'),
	path('signup', views.signup, name='signup'),
	path('media', views.media, name='media'),
	path('login', views.signin, name='login'),
	path('logout', auth_views.LogoutView.as_view(), {'next_page': '/login'}, name='logout'),
	path('dashboard', views.dashboard , name='dashboard'),
	path('search', views.searchProduct, name='search'),
	path('addProduct', views.addProduct, name='addProduct'),
	path('productPage/<int:product_id>/', views.productPage, name='productPage'),
	path('wishlist', views.wishlist, name='wishlist'),
	path('addWishlist/<int:product_id>', views.addWishlist, name='addWishlist'),
	path('deletefromWishlist/<int:product_id>', views.deletefromWishlist, name='deletefromWishlist'),
	path('requestSeller/<int:product_id>', views.requestSeller, name='requestSeller'),
	path('orderHistory', views.orderHistory, name='orderHistory'),
	path('myPosts', views.myPosts, name='myPosts'),
	path('deletePost/<int:product_id>', views.deletePost, name='deletePost'),
]