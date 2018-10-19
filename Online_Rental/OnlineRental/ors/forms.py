from django import forms
from .models import *

class ProductForm(ModelForm):
	class Meta:
		model = Product
		fields = ['name', 'description', 'category', 'price', 'duration', 'quantity', 'ptype']