from django.shortcuts import render, redirect

from .forms import CreatePost


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
        return render(request, 'blog/new_post.html', {'title': 'New Post', 'form': form})
