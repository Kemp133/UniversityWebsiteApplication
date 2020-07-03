from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='blog-index_view'),
    path('posts/new/', views.blog_new_view, name='blog-new-view')
]
