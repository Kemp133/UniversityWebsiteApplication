from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='blog-index_view'),
    path('posts/details/<uuid:pk>', views.blog_post_details, name='blog-post_details'),
    path('posts/new/', views.blog_new_view, name='blog-new-view'),
    path('posts/test', views.blog_test, name='blog-test'),
    path('posts/new/image-upload', views.blog_upload_image, name='blog-add-image')
]
