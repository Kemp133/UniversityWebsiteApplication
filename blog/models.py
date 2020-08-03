import os
import uuid

from django.db import models
from UniversityWebsiteApplication.settings import MEDIA_ROOT

# Create your models here.
from django.utils.deconstruct import deconstructible


class Blog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=128)
    raw_body_location = models.CharField(max_length=128)
    html_fragment_location = models.CharField(max_length=128)
    date_finished = models.DateTimeField()
    date_to_publish = models.DateTimeField(null=True)
    active = models.BooleanField(default=True)


class Tags(models.Model):
    tag = models.CharField(max_length=32)


class BlogTags(models.Model):
    blog_ID = models.ForeignKey(Blog, on_delete=models.CASCADE)
    tag_ID = models.ForeignKey(Tags, on_delete=models.DO_NOTHING)


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
    image = models.ImageField(upload_to=UploadToPathAndRename(os.path.join(MEDIA_ROOT, 'temp/')))

    def __str__(self):
        return ("Caption: " + self.caption + "\n"
                + "Image Path: " + self.image.path + "\n"
                + "Image Width:" + str(self.image.width) + "\n"
                + "Image Height:" + str(self.image.height) + "\n")
