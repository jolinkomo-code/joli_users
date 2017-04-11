from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from ..models.user_profile import UserProfile
from ..serializers.user_profile_serializer import UserProfileSerializer

class UserProfileView(APIView):
    def post(self, request, format= None):
        data = JSONParser().parse(request)
        user_profile_s = UserProfileSerializer(data=data)

        if user_profile_s.is_valid():
            user_profile_s.save()
            return JsonResponse(UserProfile.objects.filter(user_id=user_profile_s.data['user']).first().id, status=200, safe=False)

        return JsonResponse(user_profile_s.errors, status=400)
