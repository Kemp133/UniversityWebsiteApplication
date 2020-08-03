from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import CreatePost, UploadImage
from .models import *


# Create your views here.
def index_view(request):
    return render(request, 'blog/index.html', {'title': 'Blog'})


def blog_new_view(request):
    if request.method == "POST":
        form = CreatePost(request.POST)

        if form.is_valid():
            data = request.POST.copy()

            print(data.get('blog_title'), data.get('body'))
            return redirect('blog-index_view')
    else:
        form = CreatePost()
        image_upload_form = UploadImage()
        return render(request, 'blog/new_post.html', {'title': 'New Post',
                                                      'form': form,
                                                      'imageUploadForm': image_upload_form})


def blog_test(request):
    form = UploadImage()
    return render(request, 'blog/test.html', {'title': 'Test', 'form': form})


def blog_upload_image(request):
    if request.is_ajax() and request.method == 'POST':
        form = UploadImage(request.POST, request.FILES)

        if form.is_valid():
            new_image = BlogImageUpload()
            new_image.caption = form.cleaned_data['caption']
            new_image.image = form.cleaned_data['image']
            # print(new_image)
            new_image.save()
            last_obj = BlogImageUpload.objects.latest('id')
            return JsonResponse({'result': 'success',
                                 'file_name': str(last_obj.image.file).split('/')[-1]})
        else:
            return JsonResponse({'result': 'error',
                                 'message': 'File failed to upload!'})
