from rest_framework import serializers
from ..models.user_photos import UserPhotos

class UserPhotoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = UserPhotos
        fields = ('image','name','user_profile')
