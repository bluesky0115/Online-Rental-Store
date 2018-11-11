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
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

		

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
	if request.user.is_authenticated:
		return HttpResponseRedirect(reverse('ors:dashboard'))
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
		feed = Product.objects.all().exclude(owner=user).order_by('postdate')
		print(type(feed))
		context=dict()
		
		context['user'] = user
		context['notifications'] = Notification.objects.filter(user=user).order_by('-timestamp')
		numbers_list = range(1, feed.count())
		page = request.GET.get('page', 1)
		paginator = Paginator(feed, 10)
		try:
			feed = paginator.page(page)
		except PageNotAnInteger:
			feed = paginator.page(1)
		except EmptyPage:
			feed = paginator.page(paginator.num_pages)
		context['feed'] = feed
		#return render(request, 'home.html', {'numbers': numbers})
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
		feed = Product.objects.none()

		if request.method == 'POST':
			query = request.POST['search']
			with connection.cursor() as cursor:
				cursor.callproc('SearchbyName', ['%'+query+'%'])
				feeds = dictfetchall(cursor)
				for i in feeds:
					lis.append(i['id'])
				feed = Product.objects.filter(id__in=lis).order_by('-postdate')
				#print(feed)
			messages.success(request, str(feed.count())+" products found !!!")
			context = dict()
			context['feed'] = feed
			context['user'] = user
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

		page = request.GET.get('page', 1)
		paginator = Paginator(feed, 10)
		try:
			feed = paginator.page(page)
		except PageNotAnInteger:
			feed = paginator.page(1)
		except EmptyPage:
			feed = paginator.page(paginator.num_pages)
		context = dict()
		context['feed'] = feed
		context['user'] = user
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
				image = request.FILES.getlist('image')
				name = request.POST.get('name')
				description = request.POST['desc']
				quantity = request.POST['quantity']
				price = request.POST.get('price')
				period = request.POST.get('period')
				category = request.POST['category']
				ptype = request.POST['ptype']
				image_r=image[0]
				print(period)
				print(image, "naya wala")
				pr = Product(owner=owner, name=name, image=image_r, description=description, category=category, quantity=quantity,
								period=period, price=price, ptype=ptype, created_by=user.email, created_at=datetime.datetime.now())
				pr.save()
				
				for i in range(len(image)):
					pro = ProductImage(product=pr, owner=owner, image=image[i] )
					print(pro)
					pro.save()
				messages.success(request, "Product successfully added !!!")
				return HttpResponseRedirect(reverse('ors:dashboard'))
			else:
				print("No image")
				messages.error(request, "Please select an image for the Product.")
				return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def productPage(request, product_id):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		product = Product.objects.get(id=product_id)
		feed = ProductRating.objects.filter(product=product)
		images = ProductImage.objects.filter(product=product_id)
		length = []
		for i in range(len(images)):
			length.append(i+1)
		if len(length):
			length.pop()
		
		if len(images) == 2:
			images=images[:1]
		elif len(images) > 2:
			images = images[0:1]+images[2:]
		elif len(images) == 0:
			images = []
		if len(images) == 0:
			images = []
		context = dict()
		print(images, length, " images multiple testing")
		context['product'] = product
		context['feed'] = feed
		context['user'] = user
		context['images'] = images
		context['length'] = length
		form = ReportForm()
		context['form']=form
		return render(request, 'product_detail.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def wishlist(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Wishlist.objects.filter(user=user).order_by('-timestamp')
		notifications = Notification(user=user, message='request')
		notifications.save()
		page = request.GET.get('page', 1)
		paginator = Paginator(feed, 2)
		try:
			feed = paginator.page(page)
		except PageNotAnInteger:
			feed = paginator.page(1)
		except EmptyPage:
			feed = paginator.page(paginator.num_pages)
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
		user = UserProfile.objects.get(email=request.user.email)
		product = Wishlist.objects.get(user=user, product=item)
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
		quantity = 1
		if request.method == "POST":
			quantity = request.POST['quantity']
		print("quantity" , quantity)
		if product.quantity > 0:
			exist = RequestSeller.objects.filter(buyer=buyer, product=product, seller=seller).count()
			if (exist == 0) and (product.owner != buyer):
				req = RequestSeller(buyer=buyer, seller=seller, product=product,quantity=quantity, timestamp=datetime.datetime.now(), created_by=buyer.email, created_at=datetime.datetime.now())
				req.created_by = buyer.name
				req.created_at = datetime.datetime.now()
				req.save()
				history = OrderHistory(customer=buyer, seller=seller, product=product, quantity=quantity, status='requested', created_by=user.email, created_at=datetime.datetime.now())
				history.created_by = buyer.name
				history.created_at = datetime.datetime.now()
				history.save()
				print("requested")
				message = 'You have a new request for ' + product.name
				messages.success(request, "Requested the Seller")
				notify = Notification(user=seller, product=product, message=message, typ='product request')
				notify.save()
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
		print(user)
		u = UserProfile.objects.get(user=user).id
		print(u)
		if request.method == "POST":
			if "cancel" in request.POST:
				product_id = request.POST['cancel']
				OrderHistory.objects.get(customer=u, product=product_id).delete()
				RequestSeller.objects.get(buyer=u, product=product_id).delete()
				return redirect('ors:orderHistory')
			if "confirmed" in request.POST:
				product_id = request.POST['confirmed']
				order = OrderHistory.objects.get(customer=u, product=product_id)
				RequestSeller.objects.get(buyer=u, product=product_id).delete()
				order.status = "confirmed"
				order.boughtDate = datetime.datetime.now()
				order.save()
				return redirect('ors:orderHistory')
		buyer = UserProfile.objects.get(email=user.email)
		feed = OrderHistory.objects.filter(customer=buyer).order_by('-timestamp')
# 		print(feed[0], feed[0].status)
		context = dict()
		context['feed'] = feed
		context['user'] = buyer
		return render(request, 'history.html', context)

	else:
		return HttpResponseRedirect(reverse('ors:login'))


def myPosts(request):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		feed = Product.objects.filter(owner=user).order_by('-postdate')
		context = dict()
		context['feed'] = feed
		context['user'] = user
		print(feed)
		return render(request, 'managePosts.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def editPost(request, product_id):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(email=request.user.email)
		product = Product.objects.get(id=product_id)

		if request.method == 'GET':
			context = dict()
			context['user'] = user
			context['product'] = product
			return render(request, 'edit_product.html', context)

		if request.method == 'POST':
			name = request.POST.get('name')
			quantity = request.POST.get('quantity')
			ptype = request.POST.get('ptype')
			image = request.FILES.get('image')
			price = request.POST.get('price')
			category = request.POST.get('category')
			duration = request.POST.get('duration')
			description = request.POST.get('desc') 
			#print(dp,"1     ",name,"2...   ",bio)
			if name is not '':
				product.name = name
			if quantity is not '':
				product.quantity = quantity
			if ptype is not product.ptype:
				product.ptype = ptype
			if price is not '':
				product.price = price
			if category is not product.category:
				product.category = category
			if duration is not '':
				product.duration = duration
			if description is not '':
				product.description = description
			if image is not None:
				product.image = image
			product.modified_by = request.user.email
			product.modified_at = datetime.datetime.now()
			product.save()
			return HttpResponseRedirect(reverse('ors:myPosts'))
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def deletePost(request, product_id):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		user = UserProfile.objects.get(email=u.email)
		product = Product.objects.get(owner=user, id=product_id)
		product.quantity = 0
		if product.quantity == 0:
			product.status = "OutofStock"
		else:
			product.status = "InStock"
		product.save()
		# feed = Product.objects.filter(owner=user).order_by('-postdate')
		# context = dict()
		# context['feed'] = feed
		#messages.success(request, "Post successfully deleted!")
		#return render(request, 'myPosts.html', context)
		return HttpResponseRedirect(reverse('ors:myPosts'))
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
					message = 'Review of your product '+product.name+'by '+buyer.name
					notify = Notification(user=product.owner, product=product, message=message, typ='product review')
					notify.save()
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


def notificationShow(request, notification_id):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(user=request.user)
		notification = Notification.objects.get(id=notification_id)
		notification.viewed = True
		notification.save()
		
		if notification.typ == 'product request':
			return HttpResponseRedirect(reverse('ors:requests'))
		if notification.typ == 'product reject' or notification.typ == 'product approve':
			return HttpResponseRedirect(reverse('ors:orderHistory'))
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		return HttpResponseRedirect(reverse('ors:login'))
		

def distinctProducts(detail):
	product=[]
	for i in detail:
		product.append(i.product.id)
	return list(set(product))


def requests(request):
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		print(u)
		user = UserProfile.objects.get(user=u)		
		detail = RequestSeller.objects.filter(seller=user).order_by('-timestamp')
		print(detail)
		product = distinctProducts(detail)
		products=[]
		for i in product:
			products.append(Product.objects.get(id=int(i)))
		
		context = {}
		context['products'] = products
		context['requests'] = detail
		context['user'] = user
		print(context)
		return render(request, 'requested.html', context)
	else:
		return HttpResponseRedirect(reverse('ors:login'))


def approveRequest(request, req_id):
	if request.user.is_authenticated:
		user = UserProfile.objects.get(user=request.user)
		print(req_id)
		req = RequestSeller.objects.get(id=req_id)
		product = Product.objects.get(id=req.product.id)
		
		#print("+++++++++  ",req.buyer,user,req.product)
		# print(OrderHistory.objects.get(seller=user, product=req.product))
		history = OrderHistory.objects.get(customer=req.buyer, seller=user, product=req.product)
		print(history)

		if request.method == 'POST':
			quantity = request.POST['quantity']
			dateStart = request.POST.get('dateStart')
			dateEnd = request.POST.get('dateEnd')
			status = request.POST['status']
			if status == 'approve':
				product.quantity = product.quantity - int(quantity)
				if product.quantity <= 0:
					product.quantity = 0
					product.status = "OutofStock"
				product.save()
				message = 'Your request for '+req.product.name+' has been ACCEPTED by Seller! Grab it now!'
				notify = Notification(user=req.buyer, message=message, product=product, typ='product approve')
				notify.save()
				req.status = 'accepted'
				history.status = 'accepted'

			else:
				message = 'Your request for '+req.product.name+' has been DECLINED by Seller'
				notify = Notification(user=req.buyer, product=product, message=message, typ='product reject')
				notify.save()
				req.status = 'rejected'
				req.delete()
				history.status = 'rejected'

		history.modified_by = user.name
		req.modified_by = user.name
		history.modified_at = datetime.datetime.now()
		req.modified_at = datetime.datetime.now()
		history.save()
		req.save()
		print(history.status)
		return HttpResponseRedirect(reverse('ors:requests'))


def report(request):
	print("Report")
	if request.user.is_authenticated:
		u = User.objects.get(id=request.user.id)
		us = UserProfile.objects.get(user=u)
		if request.method == 'POST':
			form = ReportForm(request.POST)
			if form.is_valid():
				report_form = form.save(commit=False)
				report_form.complainant = us
				print(request.POST['product_id'])
				report_form.product = Product.objects.get(id=request.POST['product_id'])
				report_form.respondant = report_form.product.owner
				
				report_form.timestamp = datetime.datetime.now()
				report_form.created_by = us.name
				report_form.created_at = datetime.datetime.now()
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