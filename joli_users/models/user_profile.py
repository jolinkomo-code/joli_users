from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    gender = models.CharField(max_length=10, null=True)
    birth_date = models.DateField(max_length=15, null=True)
    address = models.CharField(max_length=200,null=True)
    mobile_no = models.CharField(max_length=10, null=True)
    location = models.CharField(max_length=100, null=True)
    occupation = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=200, null=True)
    mobile_no = models.CharField(max_length=20, null=True)
    interest = models.CharField(max_length=255, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
