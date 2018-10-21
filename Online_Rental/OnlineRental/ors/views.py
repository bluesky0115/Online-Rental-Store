from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login
from django_user_agents.utils import get_user_agent
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
				loginTrail(request,email,'failed')
				return HttpResponseRedirect(reverse('ors:login'))
			else:
				loginTrail(request,email,'success')
				login(request, user)
				return HttpResponsePermanentRedirect(reverse('ors:dashboard'))
		else:
			messages.error(request, 'failed')
			loginTrail(request,email,'False')
			return HttpResponseRedirect(reverse('ors:login'))


def loginTrail(request, email, status):
	email = email
	ip = request.get_host()
	server_name = request.META['SERVER_NAME']
	server_port = request.META['SERVER_PORT']
	secure = request.is_secure()
	browser = request.user_agent.browser.family +"\t"+ request.user_agent.browser.version_string

	if request.user_agent.is_pc:
		device = 'PC'
		os = request.user_agent.os.family +"\t"+ request.user_agent.os.version_string
		trail = LoginTrail(email=email,ip=ip, server_name=server_name, server_port=server_port, 
							secure=secure, status=status, browser=browser, device=device, os=os)
		trail.save()

	else:
		device = request.user_agent.device[0]
		brand = request.user_agent.device[1]
		model = request.user_agent.device[2]
		os = request.user_agent.os.family + request.user_agent.os.version_string
		trail = LoginTrail(email=email,ip=ip, server_name=server_name, server_port=server_port, 
							secure=secure, status=status, browser=browser,device=device, brand=brand,
							model=model, os=os)
		trail.save()



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

	if request.method == 'POST' and request.FILES.get('image'):
		if request.user.is_authenticated:
			user = User.objects.get(id=request.user.id)
			owner = UserProfile.objects.get(email=user.email)
			name = request.POST['name']
			description = request.POST['desc']
			price = request.POST['price']
			image = request.FILES.get('image')
			category = request.POST['category']
			ptype = request.POST['ptype']

			pr = Product(owner=owner, name=name, image=image, description=description, category=category, price=price, ptype=ptype)
			pr.save()
			return HttpResponseRedirect(reverse('ors:dashboard'))


def productPage(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		product = Product.objects.get(id=product_id)
		context = dict()
		context['product'] = product
		print(str(product.id))
		return render(request, 'productPage.html', context)


def wishlist(request):
	if request.user.is_authenticated:
		feed = Wishlist.objects.all().order_by('-timestamp')
		print(feed)
		context = dict()
		context['feed'] = feed
		return render(request, 'wishlist.html', context)


def addWishlist(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		print(user.id, user.username)
		userp = UserProfile.objects.get(email=user.email)
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
			return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
		else:
			print("hai to")
			return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))


def deletefromWishlist(request, product_id):
	if request.user.is_authenticated:
		product = Wishlist.objects.get(id=product_id)
		product.delete()
		context = dict()
		feed = Wishlist.objects.all().order_by('-timestamp')
		context['feed'] = feed
		return render(request, 'wishlist.html', context)


def requestSeller(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		product = Product.objects.get(id=product_id)
		buyer = UserProfile.objects.get(email=user.email)
		seller = product.owner
		print(request.path)

		if product.quantity > 0:
			exist = RequestSeller.objects.filter(buyer=buyer, product=product).count()
			if exist == 0:
				req = RequestSeller(buyer=buyer, seller=seller, product=product, timestamp=datetime.datetime.now())
				req.save()
				print("requested")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
				#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
			else:
				print("already requested")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
				#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
		else:
			print("OutofStock!!!")
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
			#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))


def orderHistory(request):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		buyer = UserProfile.objects.get(email=user.email)
		feed = RequestSeller.objects.filter(buyer=buyer).order_by('-timestamp')
		context = dict()
		context['feed'] = feed
		return render(request, 'orderHistory.html', context)

def myPosts(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Product.objects.filter(owner=user)
		context = dict()
		context['feed'] = feed
		return render(request, 'myPosts.html', context)


def deletePost(request, product_id):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		user = UserProfile.objects.get(email=u.email)
		product = Product.objects.get(id=product_id)
		product.delete()
		feed = Product.objects.filter(owner=user).order_by('-postdate')
		context = dict()
		context['feed'] = feed

		return render(request, 'myPosts.html', context)



def profile(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)
		
		detail = UserProfile.objects.get(user=u)
		
		context = {}
		context['detail'] = detail
		
		return render(request, 'profile_detail.html', context)