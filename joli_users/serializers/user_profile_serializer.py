from rest_framework import serializers
from ..models.user_profile import UserProfile

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'gender', 'birth_date', 'address','mobile_no','location', 'occupation','status','interest', 'user')
