import os

from django.http import JsonResponse
from django.shortcuts import render, redirect

from .forms import CreatePost, UploadImage
from .models import BlogImageUpload
from Util import BlogBodyParser as bbp

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
    string_to_use = """Start Text

\section{Test Header}
Middle text 1

\subsection{Test Subheader}
Middle text 2

\subsubsection{Test SubSubSection}
Middle Text 3

Middle text 3 2

\img{0b4a3dff96724e2d_NLKy1i2.png}"""
    print(string_to_use)
    bbp.parse_body(string_to_use)
    return render(request, 'blog/test.html', {'title': 'Test'})


def create_image_tag(name):
    return r'\img{' + str(name) + '}'


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
