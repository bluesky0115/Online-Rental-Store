
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
from .forms import ReportForm


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
		context['user'] = user
		return render(request, 'dashboard.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


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
				#return HttpResponseRedirect(reverse('ors:dashboard', kwargs={'feed':feed}))
				return render(request, 'dashboard.html', context)
		return HttpResponseRedirect(reverse('ors:dashboard'))
	else:
		return HttpResponseRedirect(reverse('ors:login'))


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
	else:
		return HttpResponseRedirect(reverse('ors:login'))



#------------------------------------------------------------------------------------------------------


def addProduct(request):
	if request.user.is_authenticated:
		if request.method == 'GET':
			if request.user.is_authenticated:
				u = UserProfile.objects.get(email=request.user.email)
				return render(request, 'postAd.html', {'user': u})

		if request.method == 'POST':
			if request.FILES.get('image'):
				user = User.objects.get(id=request.user.id)
				owner = UserProfile.objects.get(email=user.email)
				image = request.FILES.get('image')
				name = request.POST['name']
				description = request.POST['desc']
				quantity = request.POST['quantity']
				price = request.POST.get('price')
				duration = request.POST.get('duration')
				category = request.POST['category']
				ptype = request.POST['ptype']
				pr = Product(owner=owner, name=name, image=image, description=description,category=category, quantity=quantity,
								price=price, ptype=ptype, created_by=user.email, created_at=datetime.datetime.now())
				pr.save()
				messages.success(request, "Product successfully added !!!")
				return HttpResponseRedirect(reverse('ors:dashboard'))
			else:
				print("No image")
				messages.success(request, "Please select an image for the Product.")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def productPage(request, product_id):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		product = Product.objects.get(id=product_id)
		feed = ProductRating.objects.filter(product=product)
		context = dict()
		context['product'] = product
		context['feed'] = feed
		context['user'] = user
		form = ReportForm()
		context['form']=form
		return render(request, 'product_detail.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def wishlist(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Wishlist.objects.all().order_by('-timestamp')
		print(type(feed))
		context = dict()
		context['feed'] = feed
		context['user'] = user
		return render(request, 'wishlist.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


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
		print(exist, product.owner, userp)
		if exist == 0:
			if product.owner != userp:
				item = Wishlist(user=userp, product=product, status=status, quantity=quantity, timestamp=datetime.datetime.now())
				item.save()
				print("added")
				messages.success(request, "Added to Wishlist!")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
			else:
				messages.error(request, "Same user/owner")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
		else:
			print("hai to")
			messages.error(request, "Already in Wishlist!")
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def deletefromWishlist(request, product_id):
	if request.user.is_authenticated:
		item = Product.objects.get(id=product_id)
		product = Wishlist.objects.get(product=item)
		product.delete()
		context = dict()

		feed = Wishlist.objects.all().order_by('-timestamp')
		context['feed'] = feed
		messages.success(request, "Product successfully removed from your Wishlist!")
		#return render(request, 'wishlist.html', context)
		return HttpResponseRedirect(reverse('ors:wishlist'))
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def requestSeller(request, product_id):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		product = Product.objects.get(id=product_id)
		buyer = UserProfile.objects.get(email=user.email)
		seller = product.owner
		print(request.path)

		if product.quantity > 0:
			exist = RequestSeller.objects.filter(buyer=buyer, product=product).count()
			if (exist == 0) and (product.owner != buyer):
				req = RequestSeller(buyer=buyer, seller=seller, product=product, timestamp=datetime.datetime.now(), created_by=buyer.email, created_at=datetime.datetime.now())
				req.save()
				history = OrderHistory(customer=buyer, seller=seller, product=product, status='requested', created_by=user.email, created_at=datetime.datetime.now())
				history.save()
				print("requested")
				messages.success(request, "Requested the Seller")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
				#return HttpResponseRedirect(reverse('ors:productPage', kwargs={'product_id': product_id}))
			elif product.owner==buyer:
				messages.error(request, "Same user/owner")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])

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
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def orderHistory(request):
	if request.user.is_authenticated:
		user = User.objects.get(id=request.user.id)
		buyer = UserProfile.objects.get(email=user.email)
		feed = OrderHistory.objects.all().order_by('-timestamp')
		context = dict()
		context['feed'] = feed
		context['user'] = buyer
		return render(request, 'history.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def myPosts(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Product.objects.filter(owner=user)
		context = dict()
		context['feed'] = feed
		context['user'] = user
		print(feed)
		return render(request, 'managePosts.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


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
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def profile(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)		
		detail = UserProfile.objects.get(user=u)
		context = {}
		context['detail'] = detail
		return render(request, 'profile_detail.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def editProfile(request):
	if request.method == 'GET':
		if request.user.is_authenticated:
			user = UserProfile.objects.get(email=request.user.email)
			print("get")
			context = {}
			context['user'] = user
			return render(request, 'profile_edit.html', context)
		else:
			return HttpResponseRedirect(reverse('ors:login'))

	if request.method == 'POST':
		if request.user.is_authenticated:
			print('post')
			user = UserProfile.objects.get(email=request.user.email)
			name = request.POST['name']
			mobileNumber = request.POST.get('mobileNumber')
			bio = request.POST.get('bio')
			dp = request.FILES.get('image')
			print(dp,"1     ",name,"2...   ",bio)
			if name is not '':
				user.name = name
			if mobileNumber is not '':
				user.mobileNumber = mobileNumber
			if bio is not '':
				user.bio = bio
			if dp is not None:
				user.dp = dp
			user.modified_by = request.user.email
			user.modified_at = datetime.datetime.now()
			user.save()
			print()
			
			return HttpResponseRedirect(reverse('ors:profile'))

		else:
			return HttpResponseRedirect(reverse('ors:login'))


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
					return render(request, 'product_detail.html', context)

				if request.method == 'POST':
					rating = request.POST.get('rating')
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
	else:
		return HttpResponseRedirect(reverse('ors:login'))
		

def requests(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)
		user = UserProfile.objects.get(user=u)		
		detail = RequestSeller.objects.filter(seller=user)
		context = {}
		context['detail'] = detail
		context['user'] = user
		print(context)
		return render(request, 'requested.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def report(request):
	print("Report")
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		us = UserProfile.objects.get(user=u)
		print("HIIIIIIIIIII")
		if request.method == 'POST':
			form = ReportForm(request.POST)
			if form.is_valid():
				report_form = form.save(commit=False)
				report_form.complainant = us
				report_form.respondant = us
				print(request.POST['product_id'])
				report_form.product = Product.objects.get(id=request.POST['product_id'])
				
				print("Hiiiiiii")
				report_form.timestamp = datetime.datetime.now()
				report_form.created_by = us.name
				report_form.created_at = datetime.datetime.now()
				report_form.modified_by = us.name
				report_form.modified_at = datetime.datetime.now() 
				print(us,u)
				report_form.save()

				return redirect('ors:dashboard') 
			form = ReportForm()
			context={'form':form}
			#context['form'] = form
			return render(request,'product_detail.html', context=context)
		form = ReportForm()
		context={'form':form}
		#context['form'] = form
		return render(request,'product_detail.html', context=context)
		
	else:
		return HttpResponseRedirect(reverse('ors:login'))