from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='blog-index_view'),
]
