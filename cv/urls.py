from django.urls import path
from .views import index, manage


urlpatterns = [
	path("", index, name='cv-index'),
	path("manage", manage, name='cv-manage')
]
