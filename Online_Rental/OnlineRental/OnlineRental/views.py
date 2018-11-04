from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse
import requests
from ors.models import *
from django.contrib import messages
from django.contrib.auth import authenticate, login
import datetime

def direct(request):
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

def addNewUser(data):
		username = data['student'][0]['Student_First_Name']
		fullname = data['student'][0]['Student_First_Name'] + ' ' + data['student'][0]['Student_Last_name']
		email = data['student'][0]['Student_Email']
		password = "iamstudent"
		roll_no = data['student'][0]['Student_ID']
		phone_number = data['student'][0]['Student_Mobile']
		dp = 'dp/image.jpg'
		#dp = ModelWithFileField(file_field=request.FILES['file'])
		batchYear = 'UG'+data['student'][0]['Student_Cur_YearofStudy']
		gender = data['student'][0]['Student_Gender']
		user = User.objects.create_user(username=username, email=email, password=password)
		user.save()
		userp = UserProfile(user=user, name=fullname, email=email, roll_no=roll_no, mobileNumber=phone_number,
								 dp=dp, year=batchYear, gender=gender, created_by=user.email, created_at=datetime.datetime.now())
		userp.save()
			
def login_api(request,token_id):
	print(token_id)
	pay = {'token':token_id,
		'secret':"2d1c5eda8a6f6674b3973f76d94861e1637baafd5d840192f547c708f2fee2d6a4e32cdc0eb5353aaea8d7e7def12489134e32be8b8507a18d5b64c20d0267de"
	}
	url = " https://serene-wildwood-35121.herokuapp.com/oauth/getDetails"
	reponse = requests.post(url,data=pay)
	data = reponse.json()
	print(data)
	email = data['student'][0]['Student_Email']
	try:
			u = User.objects.get(email=email)
			print(u.password)
	except User.DoesNotExist:
			u = None
	if u is not None:
			username = u.username
			password = "iamstudent"
			user = authenticate(request, username=username, password=password)
			print(username,user)

			if user is None:
				messages.error(request, 'Invalid Credentials')
				loginTrail(request,email,'failed')
				return HttpResponseRedirect(reverse('ors:login'))
			else:
				loginTrail(request,email,'success')
				login(request, user)
				return HttpResponsePermanentRedirect(reverse('ors:dashboard'))
	else:
			
			loginTrail(request,email,'success')
			addNewUser(data)
			try:
				u = User.objects.get(email=email)
				print(u.password)
			except User.DoesNotExist:
				u = None
			username = u.username
			password = "iamstudent"
			user = authenticate(request, username=username, password=password)
			login(request, user)
			return HttpResponseRedirect(reverse('ors:dashboard'))