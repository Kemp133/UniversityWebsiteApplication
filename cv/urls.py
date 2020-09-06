from django.urls import path
from .views import index, manage, add_basic_information


urlpatterns = [
	path("", index, name='cv-index'),
	path("manage", manage, name='cv-manage'),
	path("manage/add/BasicInformation", add_basic_information, name='cv-add-basic-information')
]
