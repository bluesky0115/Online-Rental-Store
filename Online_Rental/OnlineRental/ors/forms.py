from django import forms
from .models import *

class ReportForm(forms.ModelForm):
    OPTIONS = (
            ("Product already sold", "Product already sold"),
            ("Seller not responding/phone unreachable", "Seller not responding/phone unreachable"),
            ("Ad is duplicate", "Ad is duplicate"),
            ("Wrong category","Wrong category"),
            ("Offensive content","Offensive content"),
            ("Fraud reason","Fraud reason"),
            )
    complain = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple,choices=OPTIONS)
    # complain = forms.CharField(label="label")
    class Meta:
    	model = Report
    	fields = ['complain']
