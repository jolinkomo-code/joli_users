from __future__ import unicode_literals
from django.db import models
from user_profile import UserProfile
from django_thumbs.db.models import ImageWithThumbsField
from django.conf import settings

class UserPhotos(models.Model):
    image = ImageWithThumbsField(upload_to=settings.JOLI_USER_PHOTOS_RELATIVE_PATH,default="imagenotfound.jpeg", max_length=254,sizes=settings.JOLI_USERS_IMAGE_THUMBNAILS)
    name = models.CharField(max_length=200,null=False)
    user_profile = models.OneToOneField(UserProfile)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
