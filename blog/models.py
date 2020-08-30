import os
import uuid

from django.db import models
from UniversityWebsiteApplication.settings import MEDIA_ROOT

# Create your models here.
from django.utils.deconstruct import deconstructible


class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=128)
    raw_body_location = models.CharField(max_length=128)
    html_fragment_location = models.CharField(max_length=128)
    date_finished = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)


class BlogPostImages(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    image_path = models.CharField(max_length=128)


class BlogImageToMove(models.Model):
    post_id = models.ForeignKey(Post, on_delete=models.CASCADE)
    temp_path = models.CharField(max_length=128)
    new_path = models.CharField(max_length=128)


class Tags(models.Model):
    tag = models.CharField(max_length=32)


@deconstructible
class UploadToPathAndRename(object):

    def __init__(self, path):
        self.sub_path = path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        # set filename as random string
        filename = '{}.{}'.format(uuid.uuid4().hex, ext)
        # return the whole path to the file
        return os.path.join(self.sub_path, filename)


class BlogImageUpload(models.Model):
    caption = models.CharField(max_length=256, blank=True)
    alt_text = models.CharField(max_length=256, blank=True)
    image = models.ImageField(upload_to=UploadToPathAndRename(os.path.join(MEDIA_ROOT, 'temp/')))

    def __str__(self):
        return ("Caption: " + self.caption + "\n"
                + "Alt_Text: " + self.alt_text + "\n"
                + "Image Path: " + self.image.path + "\n"
                + "Image Width:" + str(self.image.width) + "\n"
                + "Image Height:" + str(self.image.height) + "\n")


class BlogExceptions(models.Model):
    exc_type = models.CharField(max_length=512, blank=True)
    value = models.CharField(max_length=512, blank=True)
    traceback = models.CharField(max_length=512, blank=True)
    date_excepted = models.DateTimeField(auto_now=True)

    def __str__(self):
        print(f"Type: {self.exc_type}\nValue: {self.value}\nTraceback: {self.traceback}\nDate Occured: "
              f"{self.date_excepted}")
