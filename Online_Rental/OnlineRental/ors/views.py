from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.contrib.auth.models import User
from ors.functions.functions import handle_uploaded_file
import datetime


def index(request):
	return HttpResponse("Hello...")


def media(request):
	if request.method == 'GET':
		return render(request, 'media.html')

	if request.method == 'POST' and request.FILES['image']:
		# dp = ExampleModel(model_pic=request.FILES['image'])
		# dp.save()
		handle_uploaded_file(request.FILES['image'])
		print('hogya!')
		messages.success(request, 'Uploaded!!!')
		return HttpResponseRedirect(reverse('ors:media'))

	return render(request, 'media.html')
		


def signup(request):
	if request.method == 'GET':
		return render(request, 'signup.html')

	if request.method == 'POST' and request.FILES.get('image'):
		username = request.POST['uname']
		fullname = request.POST['fname']
		email = request.POST['email']
		password = request.POST['passwd']
		roll_no = request.POST['roll_no']
		phone_number = request.POST['phno']
		dp = request.FILES.get('image')
		#dp = ModelWithFileField(file_field=request.FILES['file'])
		batchYear = request.POST['batch']
		gender = request.POST['gender']

		try:
			if User.objects.get(email=email):
				context = dict()
				context['error_message'] = 'Email already registered!!!'
				print('firse')
				return render(request, 'signup.html', context)
		except User.DoesNotExist:
			user = User.objects.create_user(username=username, email=email, password=password)
			user.save()
			userp = UserProfile(user=user, name=fullname, email=email, roll_no=roll_no, mobileNumber=phone_number, dp=dp, year=batchYear,
                               gender=gender)
			userp.save()
			print('hogya!')
			return HttpResponseRedirect(reverse('ors:login'))
		print('kuchna')
	return render(request, 'signup.html')

def signin(request):
	if request.method == 'GET':
		return render(request, 'registration/login.html')

	if request.method == 'POST':
		email = request.POST.get('email')
		password = request.POST.get('password')
		
		
		try:
			u = User.objects.get(email=email)
			print(u.password)
		except User.DoesNotExist:
			u = None

		if u is not None:
			username = u.username
			user = authenticate(request, username=username, password=password)
			print(username)

			if user is None:
				messages.error(request, 'Invalid Cred')
				return HttpResponseRedirect(reverse('ors:login'))
			else:
				login(request, user)
				return HttpResponsePermanentRedirect(reverse('ors:dashboard'))
		else:
			messages.error(request, 'Not found')
			return HttpResponseRedirect(reverse('ors:login'))


def dashboard(request):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		feed = Product.objects.all()
		context=dict()
		context['feed'] = feed
		return render(request, 'dashboard.html', context)


def searchProduct(request):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)

		if request.method == 'POST':
			name = request.POST['search']
			sfeed = Product.objects.filter(name=name)
			context = dict()
			context['sfeed'] = sfeed
			return render(request, 'home.html', context)


def addProduct(request):
	if request.method == 'GET':
		if request.user.is_authenticated:
			return render(request, 'addProduct.html')

	if request.method == 'POST':
		if request.user.is_authenticated:
			user = User.objects.get(id=request.user.id)
			owner = UserProfile.objects.get(id=user.id)
			name = request.POST['name']
			description = request.POST['desc']
			price = request.POST['price']
			category = request.POST['category']
			ptype = request.POST['ptype']

			pr = Product(owner=owner, name=name, description=description, category=category, price=price, ptype=ptype)
			pr.save()
			return HttpResponseRedirect(reverse('ors:dashboard'))

def productPage(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		product = Product.objects.get(id=product_id)
		context = dict()
		context['product'] = product
		return render(request, 'productPage.html', context)

def addWishlist(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		userp = UserProfile.objects.get(id=user.id)
		product = Product.objects.get(id=product_id)
		quantity = product.quantity
		if quantity>0:
			status = 'InStock'
		else:
			status = 'OutofStock'

		exist = Wishlist.objects.filter(user=userp, product=product).count()
		print(exist)
		if exist == 0:
			item = Wishlist(user=userp, product=product, status=status, quantity=quantity, timestamp=datetime.datetime.now())
			item.save()
			print("added")
			return HttpResponseRedirect(reverse('ors:dashboard'))
		else:
			print("hai to")
			return HttpResponseRedirect(reverse('ors:dashboard'))

def wishlist(request):
	if request.user.is_authenticated:
		feed = Wishlist.objects.all().order_by('-timestamp')
		print(feed)
		context = dict()
		context['feed'] = feed
		return render(request, 'wishlist.html', context)