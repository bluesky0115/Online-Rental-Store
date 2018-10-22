from django.db import models 
from django.core.validators import RegexValidator
from django.contrib.auth.models import User
from datetime import datetime
from django.forms import ModelForm


def user_directory_path(instance, filename):
    name, extension = filename.split('.')
    print(extension)
    return 'dp/{0}.{1}'.format(instance.user.name, extension)

def product_directory_path(instance, filename):
    return 'products/{0}/{1}/{2}'.format(instance.owner.name, instance.name,filename)

# Create your models here.
class UserProfile(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE, default=0)
	name = models.CharField(max_length=60, blank=False)

	email_validator = RegexValidator(regex=r'^.+(iiits.in)$')
	email = models.EmailField(validators=[email_validator], max_length=60, blank=False)
	
	mobileNumber_validator = RegexValidator(regex=r'^\d{4}([- ])\d{7}|(\+91[\-\s]?)?[0]?[0-9]\d{9}$')
	mobileNumber = models.CharField(validators=[mobileNumber_validator], max_length=12, blank=True)
	
	rollNo_validator = RegexValidator(regex=r'^\d{9}$')
	roll_no = models.CharField(validators=[rollNo_validator], max_length=9, blank=False,default='000000000', help_text='Unique identifier for the student')
	
	year = models.CharField(max_length=8, choices=(
		('UG1','UG1'),('UG2','UG2'),('UG3','UG3'),('UG4','UG4'),
		('MS','MS'),('Ph.D','Ph.D'),('faculty','faculty'),('none','none')), default='none')
	
	gender = models.CharField(max_length=1, choices=(
		('M', 'Male'),('F', 'Female')), null=True)

	dp = models.FileField(upload_to=user_directory_path, blank=True)

	def __str__(self):
		return str(self.name)

class LoginTrail(models.Model):
	timestamp = models.DateTimeField(auto_now_add=True, blank=False)
	email = models.EmailField(max_length=60, blank=False)
	ip = models.CharField(max_length=32)
	status = models.CharField(max_length=10, choices=(
												('success','success'),('failed','failed')), default='failed')
	secure = models.CharField(max_length=5, choices=(
												('True','True'),('False','False')), default='False')
	server_name = models.CharField(max_length=30, default='unknown')
	server_port = models.IntegerField(default=0)
	device = models.CharField(max_length=42, default='unknown')
	model = models.CharField(max_length=42, blank=True)
	brand = models.CharField(max_length=42, blank=True)
	browser = models.CharField(max_length=42, default='unknown')
	os = models.CharField(max_length=42, default='unknown')

	def __str__(self):
		return str(self.email)+'\'s attempt'

class Product(models.Model):
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	name = models.CharField(max_length=33, blank=True)
	description = models.TextField()
	category = models.CharField(max_length=20, choices=(
												('1','electronics'),('2','stationary'),('3','fashion'),
												('4','sports'),('5', 'lifestyle'),('6', 'other')))
	price = models.FloatField()
	postdate = models.DateTimeField(auto_now_add=True, blank=False)
	duration = models.IntegerField(null=True, blank=True)
	quantity = models.IntegerField(blank=False, default=1)
	image = models.FileField(upload_to=product_directory_path, blank=False, default='default.jpg')
	ptype = models.CharField(max_length=4, choices=(
												('sell','sell'),('rent','rent'),('free','free')), default='free')

	def __str__(self):
		return str(self.name)

class Wishlist(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	status = models.CharField(max_length=10, choices=(
												('InStock','InStock'),('OutofStock','OutofStock')), default='InStock')
	quantity = models.IntegerField(blank=False, default=1)
	timestamp = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return str(self.user.name)+'\'s Wishlist'

class RequestSeller(models.Model):
	buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	seller = models.ForeignKey(UserProfile, related_name='buyer', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(default=datetime.now, blank=True)

	def __str__(self):
		return str(self.buyer.name)+'\'s request for '+str(self.product.name)

class ProductRating(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	buyer = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	rating = models.DecimalField(max_digits=2, decimal_places=1, blank=False, default=1)
	description = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True, blank=True)

	def __str__(self):
		return str(self.buyer.name)+'\'s rating of '+self.product.name

class SellerRating(models.Model):
	seller = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	buyer = models.ForeignKey(UserProfile, related_name='seller', on_delete=models.CASCADE)
	rating = models.DecimalField(max_digits=2, decimal_places=1, blank=False, default=1)
	description = models.TextField(blank=True)
	timestamp = models.DateTimeField(auto_now_add=True, blank=True)

	def __str__(self):
		return str(self.id)

class OrderHistory(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True, blank=True)
	dateStart = models.DateField()
	dateEnd = models.DateField()

	def __str__(self):
		return str(self.id)

class Report(models.Model):
	complainant = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	respondant = models.ForeignKey(UserProfile, related_name='complainant', on_delete=models.CASCADE)
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	timestamp = models.DateTimeField(auto_now_add=True, blank=True)
	complain = models.TextField()

	def __str__(self):
		return str(self.id)

class ArchivedProduct(models.Model):
	owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	description = models.TextField()
	category = models.CharField(max_length=20, choices=(
												('1','electronics'),('2','stationary'),('3','fashion'),
												('4','sports'),('5', 'lifestyle'),('6', 'other')))
	price = models.FloatField()
	postdate = models.DateTimeField(auto_now_add=True, blank=False)
	duration = models.IntegerField(blank=True)
	quantity = models.IntegerField(blank=False, default=1)
	ptype = models.CharField(max_length=4, choices=(
												('1','sell'),('2','rent')), default='1')

	def __str__(self):
		return str(self.id)


class ExampleModel(models.Model):
	model_pic = models.ImageField()
