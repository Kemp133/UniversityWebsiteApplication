from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='blog-index_view'),
    path('posts', views.index_view),
    path('posts/details/<uuid:pk>', views.blog_post_details, name='blog-post_details'),
    path('posts/manage', views.blog_manage_posts, name='blog-manage-posts'),
    path('posts/manage/delete/<uuid:pk>', views.blog_delete_post, name='blog-delete_post'),
    path('posts/manage/toggleactive/<uuid:pk>', views.blog_toggle_active, name='blog-toggle-active'),
    path('posts/new/', views.blog_new_view, name='blog-new-view'),
    path('posts/new/image-upload', views.blog_upload_image, name='blog-add-image'),
    path('posts/test', views.blog_test, name='blog-test'),
]
