from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import BasicInformation


# Create your views here.
def index(request):
	return render(request, "cv/index.html", {'title': 'My CV'})


def manage(request):
	return render(request, "cv/manage.html", {'title': 'Manage CV'})


def add_basic_information(request):
	if request.method == "POST":
		info_name = request.POST.get('info_name', '')
		info_value = request.POST.get('info_value', '')

		basic_info = BasicInformation()
		basic_info.information_name = info_name
		basic_info.information_value = info_value
		basic_info.save()

		return redirect('cv-manage', permanent=True)

	return render(request, 'cv/add_basic_information.html', {'title': 'Add Basic Information'})
