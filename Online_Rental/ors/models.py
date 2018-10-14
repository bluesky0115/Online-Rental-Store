from django.db import models

# Create your models here.
class User(models.Model):
	name = models.CharField(max_length=20, blank=False)
	email = models.EmailField(max_length=20, blank=False)
	password = models.CharField(max_length=20, blank=False)

	def __str__(self):
		return str(self.id)
		