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


def create_image_tag(name):
    return '\\img{' + str(name) + '}'


def blog_upload_image(request):
    # Check request is AJAX call, and that method is POST
    if request.is_ajax() and request.method == 'POST':
        form = UploadImage(request.POST, request.FILES)

        if form.is_valid():
            # Create a new BlogImageUpload object
            new_image = BlogImageUpload()

            # Set data in new object reference
            new_image.caption = form.cleaned_data['caption']
            new_image.image = form.cleaned_data['image']
            new_image.alt_text = form.cleaned_data['alt_text']
            # print(new_image)

            # Save the new instance
            new_image.save()

            # Retrieve the new instance from the database (to return name to form so that the image can be linked to
            # this post)
            last_obj = BlogImageUpload.objects.latest('id')

            # Format the return image name into the correct tag format so that this code isn't in the JS included with
            # the website
            file_name = str(last_obj.image.file).split('/')[-1]
            image_tag = create_image_tag(file_name)

            return JsonResponse({'result': 'success',
                                 'image_tag': image_tag})
        else:
            return JsonResponse({'result': 'error',
                                 'message': 'File failed to upload!'})
