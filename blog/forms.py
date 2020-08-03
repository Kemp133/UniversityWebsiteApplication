from django import forms
from django.forms import ModelForm

from .models import BlogImageUpload


class CreatePost(forms.Form):
    blog_title = forms.CharField(label='Post Title:', max_length=150)
    body = forms.CharField(label='Body:', widget=forms.Textarea)

    def __str__(self):
        return "Title: " + self.cleaned_data['blog_title'] + "\n" + "Body: " + self.cleaned_data['body']


class UploadImage(ModelForm):
    class Meta:
        model = BlogImageUpload
        fields = ['caption', 'image']