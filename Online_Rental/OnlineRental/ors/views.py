
from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login
from django_user_agents.utils import get_user_agent
from django.contrib import messages
from django.urls import reverse
from .models import *
from django.contrib.auth.models import User
import datetime
from django.db import connection


feed = Product.objects.none()

def index(request):
	return HttpResponse("Hello...")
		

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
			userp = UserProfile(user=user, name=fullname, email=email, roll_no=roll_no, mobileNumber=phone_number,
								 dp=dp, year=batchYear, gender=gender, created_by=user.email, created_at=datetime.datetime.now())
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
				messages.error(request, 'Invalid Credentials')
				loginTrail(request,email,'failed')
				return HttpResponseRedirect(reverse('ors:login'))
			else:
				loginTrail(request,email,'success')
				login(request, user)
				return HttpResponsePermanentRedirect(reverse('ors:dashboard'))
		else:
			messages.error(request, 'User not registered')
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
		print(request.user.email)
		user = UserProfile.objects.get(email=request.user.email)
		feed = Product.objects.all().exclude(owner=user)
		print(type(feed))
		context=dict()
		context['feed'] = feed
		return render(request, 'dashboard.html', context)


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]
#----------------------------------------------------------------------------------------------------

def searchProduct(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		lis=[]

		if request.method == 'POST':
			query = request.POST['search']
			with connection.cursor() as cursor:
				cursor.callproc('SearchbyName', ['%'+query+'%'])
				feeds = dictfetchall(cursor)
				for i in feeds:
					lis.append(i['id'])
				feed = Product.objects.filter(id__in=lis)
				#print(feed)
				context = dict()
				context['feed'] = feed
				messages.success(request, str(feed.count())+" products found !!!")
				return render(request, 'dashboard.html', context)

def searchTag(request, tag):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		uid = user.id
		print(tag)

		if tag == 'newest':
			#feed = feed.order_by('-postdate')
			feed = Product.objects.raw('SELECT * FROM ors_product WHERE NOT(owner_id=%s) ORDER BY postdate DESC', [uid])

		if tag == 'pricelow2high':
			#feed = Product.objects.all().exclude(owner=user).order_by('price')
			feed = Product.objects.raw('SELECT * FROM ors_product WHERE NOT(owner_id=%s) ORDER BY price', [uid])

		if tag == 'pricehigh2low':
			#feed = Product.objects.all().exclude(owner=user).order_by('-price')
			feed = Product.objects.raw('SELECT * FROM ors_product WHERE NOT(owner_id=%s) ORDER BY price DESC', [uid])

		if tag == 'free':
			feed = Product.objects.raw('SELECT * from ors_product WHERE ptype=%s', [tag])
			#feed = Product.objects.filter(ptype=tag).exclude(owner=user)

		context = dict()
		context['feed'] = feed
		return render(request, 'dashboard.html', context)



#------------------------------------------------------------------------------------------------------


def addProduct(request):
	if request.user.is_authenticated:
		if request.method == 'GET':
			if request.user.is_authenticated:
				return render(request, 'postAd.html')

		if request.method == 'POST':
			if request.FILES.get('image'):
				user = User.objects.get(id=request.user.id)
				owner = UserProfile.objects.get(email=user.email)
				image = request.FILES.get('image')
				name = request.POST['name']
				description = request.POST['desc']
				price = request.POST['price']
				duration = request.POST['duration']
				category = request.POST['category']
				ptype = request.POST['ptype']
				pr = Product(owner=owner, name=name, image=image, description=description,category=category, 
								price=price, ptype=ptype, created_by=user.email, created_at=datetime.datetime.now())
				pr.save()
				messages.success(request, "Product successfully added !!!")
				return HttpResponseRedirect(reverse('ors:dashboard'))
			else:
				print("No image")
				messages.success(request, "Please select an image for the Product.")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])


def productPage(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		product = Product.objects.get(id=product_id)
		feed = ProductRating.objects.filter(product=product)
		context = dict()
		context['product'] = product
		context['feed'] = feed
		
		return render(request, 'product_detail.html', context)


def wishlist(request):
	if request.user.is_authenticated:
		feed = Wishlist.objects.all().order_by('-timestamp')
		print(type(feed))
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
		if (exist == 0) and (product.owner is not userp):
			item = Wishlist(user=userp, product=product, status=status, quantity=quantity, timestamp=datetime.datetime.now())
			item.save()
			print("added")
			messages.success(request, "Added to Wishlist!")
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
		else:
			print("hai to")
			messages.error(request, "Already in Wishlist!")
			return HttpResponseRedirect(request.META['HTTP_REFERER'])


def deletefromWishlist(request, product_id):
	if request.user.is_authenticated:
		product = Wishlist.objects.get(id=product_id)
		product.delete()
		context = dict()
		feed = Wishlist.objects.all().order_by('-timestamp')
		context['feed'] = feed
		messages.success(request, "Product successfully removed from your Wishlist!")
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
			if (exist == 0) and (product.owner is not buyer):
				req = RequestSeller(buyer=buyer, seller=seller, product=product, timestamp=datetime.datetime.now(), created_by=buyer.email, created_at=datetime.datetime.now())
				req.save()
				history = OrderHistory(customer=buyer, seller=seller, product=product, status='requested', created_by=user.email, created_at=datetime.datetime.now())
				history.save()
				print("requested")
				messages.success(request, "Requested the Seller")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
				#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
			else:
				print("already requested")
				messages.warning(request, "Product already requested! Please wait for seller to repond.")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
				#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
		else:
			print("OutofStock!!!")
			messages.success(request, "Sorry! Product is currently OutofStock.")
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
			#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))


def orderHistory(request):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		buyer = UserProfile.objects.get(email=user.email)
		feed = OrderHistory.objects.all().order_by('-timestamp')
		context = dict()
		context['feed'] = feed
		return render(request, 'history.html', context)


def myPosts(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Product.objects.filter(owner=user)
		context = dict()
		context['feed'] = feed
		print(feed)
		return render(request, 'managePosts.html', context)


def deletePost(request, product_id):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		user = UserProfile.objects.get(email=u.email)
		product = Product.objects.get(id=product_id)
		product.delete()
		feed = Product.objects.filter(owner=user).order_by('-postdate')
		context = dict()
		context['feed'] = feed
		messages.success(request, "Post successfully deleted!")
		return render(request, 'myPosts.html', context)


def profile(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)		
		detail = UserProfile.objects.get(user=u)
		context = {}
		context['detail'] = detail
		return render(request, 'profile_detail.html', context)


def editProfile(request):
	if request.method == 'GET':
		if request.user.is_authenticated:
			print('get')
			return render(request, 'profile_edit.html')

	if request.method == 'POST':
		if request.user.is_authenticated:
			print('post')
			user = UserProfile.objects.get(email=request.user.email)
			name = request.POST['name']
			mobileNumber = request.POST['mobileNumber']


			if str(name) is not '':
				user.name = name
			if str(mobileNumber) is not '':
				user.mobileNumber = mobileNumber
			user.modified_by = request.user.email
			user.modified_at = datetime.datetime.now()
			user.save()
			print('gya')
			return HttpResponseRedirect(reverse('ors:profile'))


def rateProduct(request, product_id):
	if request.user.is_authenticated:
		buyer = UserProfile.objects.get(email=request.user.email)
		product = Product.objects.get(id=product_id)
		context=dict()
		context['product_id']=product_id

		if RequestSeller.objects.filter(product=product).count()>0:
			if (ProductRating.objects.filter(buyer=buyer, product=product).count()==0):
				if request.method == 'GET':
					print('get')
					return render(request, 'rateProduct.html', context)

				if request.method == 'POST':
					rating = request.POST['rating']
					comment = request.POST['comment']
					print('post')
					review = ProductRating(buyer=buyer, product=product, rating=rating, description=comment, created_by=request.user.email, created_at=datetime.datetime.now())
					review.save()
					messages.success(request, "Thanks for your review !")
					return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id':product_id}))
			else:
				print("baar baar nhi...")
				messages.warning(request, "You have already reviewed this Product")
				return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id':product_id}))

		else:
			print("pahle istemaal kare fir vichaar bate!!!")
			messages.error(request, "Can't review Products you haven't used.")
			return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id':product_id}))
		

def requests(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)
		us = UserProfile.objects.get(user=u)		
		detail = RequestSeller.objects.filter(seller=us)
		context = {}
		context['detail'] = detail
		print(context)
		return render(request, 'requested.html', context)