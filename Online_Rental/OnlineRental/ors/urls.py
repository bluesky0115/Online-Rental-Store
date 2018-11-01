
from django.urls import path,include,re_path
from django.contrib.auth import views as auth_views
#from django.contrib.auth import LogoutView
from django.views.generic.base import TemplateView
from . import views

app_name = 'ors'

urlpatterns = [
	path('', views.index, name='index'),
	path('signup', views.signup, name='signup'),
	path('login', views.signin, name='login'),
	path('logout', auth_views.LogoutView.as_view(), {'next_page': '/login'}, name='logout'),
	path('dashboard', views.dashboard , name='dashboard'),
	path('search', views.searchProduct, name='search'),
	path('searchTag/<slug:tag>', views.searchTag, name='searchTag'),
	path('addProduct', views.addProduct, name='addProduct'),
	path('productPage/<int:product_id>/', views.productPage, name='productPage'),
	path('wishlist', views.wishlist, name='wishlist'),
	path('addWishlist/<int:product_id>', views.addWishlist, name='addWishlist'),
	path('deletefromWishlist/<int:product_id>', views.deletefromWishlist, name='deletefromWishlist'),
	path('requestSeller/<int:product_id>', views.requestSeller, name='requestSeller'),
	path('history', views.orderHistory, name='orderHistory'),
	path('myPosts', views.myPosts, name='myPosts'),
	path('editPost/<int:product_id>', views.editPost, name='editPost'),
	path('deletePost/<int:product_id>', views.deletePost, name='deletePost'),
	path('profile',views.profile, name='profile'),
	path('editProfile', views.editProfile, name='editProfile'),
	path('rateProduct/<int:product_id>', views.rateProduct, name='rateProduct'),
	path('requests', views.requests, name="requests"),
	path('report', views.report, name="report"),

]