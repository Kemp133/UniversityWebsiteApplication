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

			# Create a blog instance, and save it to get an ID for the current blog
			post = Post(title=blog_title, active=True)
			post.save()

			parsed_body = bbp.parse_body("\r\n", blog_body, post)

			""" Move the images (if any) that were referenced in the body to their final static location """
			move_images_to_media_root(post)

			""" Save the body to a HTML file so that it can be loaded when somebody goes to view it, as well as the raw
			 	text that makes up the body of the blog """
			files_created_successfully = _save_html_and_body_string_to_file(raw_body=blog_body, blog_post=post,
																			html_string=parsed_body)

			if files_created_successfully:
				post.save()

			return redirect('blog-index_view')
	else:
		form = CreatePost()
		image_upload_form = UploadImage()
		return render(request, 'blog/new_post.html',
					  {'title': 'New Post', 'form': form, 'imageUploadForm': image_upload_form})


def blog_test(request):
	string_to_use = \
		r"""\section{Hope}
This is the first true test of my programming prowess, as I think I've just added all the required code to finally have it create the blog post correctly and then store all of the required files in the correct places, I guess we'll find out if it works or not

While I'm at it, let's try and test the parser a little bit too. While I'm not going to go out of my way to break it \b{(as even though I've tried to program it as anybody would be using it, I'm the only one who's going to be realistically using this in the near future, and anyways, I can always make it much better after the submission and marking)}, I will try and test how good the parser is working

\subsection{Testing the subsection functionality}
This next section is a subsection, and while only the CSS styling will visually show this, I just want to test that the HTML code generated is correct and giving the correct formatting.

\subsubsection{Testing the other tags I've implemented (so far)}
The current date is the 24/08/2020, so below will be some examples of the tags I've managed to implement up to now. Who knows, maybe this blog won't last very long anyways, but at least I can show what I've managed to achieve for the submission. Thinking about what I'm about to do, I can already think of a problem with the parser, so I'll go and check this problem before I "save" the post, as it might not be a problem after all but it's best to be sure of this:

\b{Bold Text}

\i{Italic Text}

\u{Underlined Text}

\st{Struck Through Text}

\img{eafcfc9c09c94651_dRn0b2l.png}

\url{https://www.google.com, this is a test of the URL tag, it will take the user to google}

\subsection{Testing going back up a section}
While writing the URL test, I also realised I haven't tested the URL tag yet, so I will check the code for that too before I save the post as well.

\section{Final Thoughts}
If it makes it to here, I guess it's working (or at least a little bit). Hopefully everything formats correctly, though that can always be sorted out with some CSS and optimisation of the parser, so that's nothing to worry about.

I've spent an absolutely stupendous amount of time on this, and frankly if it doesn't work I'm going to be quite annoyed honestly. Hopefully the effort I've put into this system will shine through and will blind the person assessing my website with how amazing it is \i{(or at least I can hope lol)}.

Once again, writing this final section, I've realised I may have another problem, so I guess I'll add that to the list of things to check before I submit this."""
	# test = bbp.parse_body(string_to_use, debug=True)
	test = bbp.parse_body(string_to_use)
	print(test)
	return render(request, 'blog/test.html', {'title': 'Test', 'body': test})


def create_image_tag(name):
	return r'\img{' + str(name) + '}'


def move_images_to_media_root(blog_post: Post):
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
	try:
		with open(path_to_write, "w") as fos:
			fos.write(data_to_write)
	except OSError:
		report_exception()
		return False
	else:
		return True


def _move_image_to_media_root(old_path: str, new_path: str):
	# Get the directory structure to create ready to try and create it
	new_image_directory = "/".join(new_path.split("/")[:-1])

	try:
		# Attempt to create the new directory if it doesn't exist already
		if not os.path.exists(new_image_directory):
			os.makedirs(new_image_directory)
	except OSError:
		# Creating the directory structure, set up log system to report the exact error with this at a later point
		report_exception()
		return False
	else:
		# Move the image to the newly created directory
		os.rename(old_path, new_path)

	return True


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
