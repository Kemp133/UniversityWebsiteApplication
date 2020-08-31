from django.shortcuts import render, redirect
from django.contrib.auth import logout as lo


# Create your views here.
def logout(request):
	lo(request)
	return redirect('/', permanent=True)