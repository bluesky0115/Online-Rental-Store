from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.urls import reverse

def direct(request):
	return HttpResponseRedirect(reverse('ors:login'))

