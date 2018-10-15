from django.urls import path,include
from django.contrib.auth import views as auth_views
from django.views.generic.base import TemplateView
from . import views

app_name = 'ors'

urlpatterns = [
	path('', views.index, name='index'),
	path('login', views.signin, name='login'),
	path('logout', auth_views.LogoutView.as_view(), {'next_page': '/login'}, name='logout')
]