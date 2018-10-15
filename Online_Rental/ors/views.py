from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.contrib.auth.models import User


def index(request):
	return HttpResponse("Hello...")

def signin(request):
	if request.method == 'GET':
		return render(request, 'registration/login.html')

	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		print(email)
		#print(user)
		
		try:
			u = User.objects.get(email=email)
			print(u)
		except User.DoesNotExist:
			u = None
		#u = get_object_or_404(User, email=email)
		print(u)
		if u is not None:
			username = u.username
			user = authenticate(request, username=username, password=password)
			print(username)

			if user is None:
				messages.error(request, 'Invalid Credentials')
				return HttpResponseRedirect(reverse('ors:login'))
			else:
				login(request, user)
				return render(request, 'home.html', {})
		else:
			messages.error(request, 'Not found')
			return HttpResponseRedirect(reverse('ors:login'))