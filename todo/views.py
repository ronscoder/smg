from django.shortcuts import render
from django.http import HttpResponse
from .models import *
# Create your views here.

def index(request):
#	return HttpResponse("hello")
#	return render(request,'todo/index.html')
	posts = Post.objects.all()
	context = {'posts': posts}
	return render(request,'todo/index.html', context)
	
