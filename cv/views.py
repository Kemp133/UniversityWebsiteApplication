from django.shortcuts import render


# Create your views here.
def index(request):
	return render(request, "cv/index.html", {'title': 'My CV'})


def manage(request):
	pass
