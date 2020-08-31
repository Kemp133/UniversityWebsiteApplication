import os
from uuid import uuid4

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import CreatePost, UploadImage
from .models import BlogImageUpload, Post, BlogImageToMove, BlogPostImages
from .Util import BlogBodyParser as bbp
from .Util.Exceptions import report_exception

from GenericUtils import media_utils


# Create your views here.
def index_view(request):
	posts = Post.objects.filter(active=True)
	return render(request, 'blog/index.html', {'title': 'Blog', 'posts': posts})


def blog_post_details(request, pk):
	post = get_object_or_404(Post, pk=pk)

	body = _get_blog_body(post)

	return render(request, "blog/post_details.html", {'post': post, 'post_body': body})


def _get_blog_body(post: Post):
	try:
		with open(post.html_fragment_location, "r") as fis:
			body = fis.read()
	except OSError:
		report_exception()
	else:
		return body


@login_required
def blog_new_view(request):
	if request.method == "POST":
		form = CreatePost(request.POST)

		if form.is_valid():
			data = request.POST.copy()
			blog_title = data.get('blog_title')
			blog_body = data.get('body')
			blog_synopsis = data.get('synopsis')

			# Create a blog instance, and save it to get an ID for the current blog
			post = Post(title=blog_title, synopsis=blog_synopsis, active=True)
			post.save()

			parsed_body = bbp.parse_body(blog_body, post)

			""" Move the images (if any) that were referenced in the body to their final static location """
			__move_images_to_media_root(post)

			""" Save the body to a HTML file so that it can be loaded when somebody goes to view it, as well as the raw
			 	text that makes up the body of the blog """
			files_created_successfully = _save_html_and_body_string_to_file(raw_body=blog_body, blog_post=post,
																			html_string=parsed_body)

			if files_created_successfully:
				post.save()

			return redirect('blog-index_view', permanent=True)
	else:
		form = CreatePost()
		image_upload_form = UploadImage()
		return render(request, 'blog/new_post.html',
					  {'title': 'New Post', 'form': form, 'imageUploadForm': image_upload_form})


def blog_test(request):
	return render(request, 'blog/test.html', {'title': 'Test'})


def create_image_tag(name):
	return r'\img{' + str(name) + '}'


@login_required
def blog_manage_posts(request):
	all_posts = Post.objects.all()
	return render(request, 'blog/manage_posts.html', {'title': "Manage posts", 'posts': all_posts})


@login_required
def blog_toggle_active(request, pk: uuid4):
	post = get_object_or_404(Post, pk=pk)
	post.active = not post.active
	post.save()
	return redirect('/blog/posts/manage')


@login_required
def blog_delete_post(request, pk: uuid4):
	post = get_object_or_404(Post, pk=pk)

	if request.method == "POST":
		html_fragment = post.html_fragment_location
		raw_body = post.raw_body_location

		media_utils.delete_file_in_media([html_fragment, raw_body])

		post.delete()

		return redirect('blog-manage-posts', permanent=True)

	return render(request, 'blog/delete_post.html', {'title': 'Delete Blog Post', 'post': post})


def __move_images_to_media_root(blog_post: Post):
	# Get a list of all the objects with the current post's ID
	images_to_move = BlogImageToMove.objects.filter(post_id=blog_post.id)

	for image in images_to_move:
		# Create a new tuple to pass to the move image method
		temp_path, new_path = image.temp_path, image.new_path

		# Call the method, capturing the return value of the method
		success = _move_image_to_media_root(temp_path, new_path)

		# If the method is successful in moving the image, then delete the entry in the database
		if success:
			# Keep a reference to this image, so that in the future if the blog post is deleted, the related images can
			# be removed at the same time
			blog_image = BlogPostImages(post_id=blog_post, image_path=image.new_path)
			blog_image.save()
			# Delete the image from the table as it's been moved now
			image.delete()


def _save_html_and_body_string_to_file(raw_body: str, blog_post: Post, html_string: str):
	# Firstly, get the required path to the correct location to store the HTML fragment
	html_fragment_path = media_utils.get_new_path_in_media_root(f"{str(blog_post.id)}.html")
	raw_body_path = media_utils.get_new_path_in_media_root(f"{str(blog_post.id)}.txt")

	if _write_file(html_fragment_path, str(html_string)) and _write_file(raw_body_path, raw_body):
		blog_post.html_fragment_location = html_fragment_path
		blog_post.raw_body_location = raw_body_path
		blog_post.save()
		return True
	else:
		return False


def _write_file(path_to_write: str, data_to_write: str):
	# If the path does not exist, then create it
	if not os.path.exists(path_to_write):
		to_create = "/".join(path_to_write.split("/")[:-1])
		__create_directory_structure(to_create)

	# Save the files to disk
	try:
		with open(path_to_write, "w") as fos:
			fos.write(data_to_write)
	except OSError:
		report_exception()
		return False
	else:
		return True


def __create_directory_structure(path_to_create: str):
	try:
		if not os.path.exists(path_to_create):
			os.makedirs(path_to_create)
	except OSError:
		report_exception()
		return False
	else:
		return True


def _move_image_to_media_root(old_path: str, new_path: str):
	# Get the directory structure to create ready to try and create it
	new_image_directory = "/".join(new_path.split("/")[:-1])

	# If the directory can be created (or already exists), then move the file to the new location
	if __create_directory_structure(new_image_directory):
		os.rename(old_path, new_path)
		return True
	else:
		return False


@login_required
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

			# Save the new instance
			new_image.save()

			# Retrieve the new instance from the database (to return name to form so that the image can be linked to
			# this post)
			last_obj = BlogImageUpload.objects.latest('id')

			# Format the return image name into the correct tag format so that this code isn't in the JS included with
			# the website
			file_name = str(last_obj.image.file).split('/')[-1]
			image_tag = create_image_tag(file_name)

			return JsonResponse({'result': 'success', 'image_tag': image_tag})
		else:
			return JsonResponse({'result': 'error', 'message': 'File failed to upload!'})
