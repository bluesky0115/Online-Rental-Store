from django.db import models 
from django.core.validators import RegexValidator
from datetime import datetime

# Create your models here.
class UserProfile(models.Model):
	name = models.CharField(max_length=20, blank=False)
	email = models.EmailField(max_length=60, blank=False)
	mobileNumber_validator = RegexValidator(regex=r'^\d{4}([- ])\d{7}|(\+91[\-\s]?)?[0]?[0-9]\d{9}$')
	mobileNumber = models.CharField(validators=[mobileNumber_validator], max_length=12, blank=True)
	rollNo_validator = RegexValidator(regex=r'^\d{9}$')
	roll_no = models.CharField(validators=[rollNo_validator], max_length=9, blank=False,default='000000', help_text='Unique identifier for the student')
	year = models.CharField(max_length=8, choices=(
		('UG1','UG1'),('UG2','UG2'),('UG3','UG3'),('UG4','UG4'),
		('MS','MS'),('Ph.D','Ph.D'),('faculty','faculty'),('none','none')), default='none')
	gender = models.CharField(max_length=1, choices=(
		('M', 'Male'),('F', 'Female')), null=True)

	def __str__(self):
		return str(self.name)

class LoginTrail(models.Model):
	user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
	time = models.DateTimeField(auto_now_add=True, blank=False)
	email = models.EmailField(max_length=60, blank=False)
	ip = models.CharField(max_length=32)

	def __str__(self):
		return str(self.email)+"\t"+str(self.time)+"\t"+str(ip)
		