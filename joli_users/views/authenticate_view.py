from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny

class Authenticate(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        data = JSONParser().parse(request)

        if 'username' not in data:
            return JsonResponse('username is required', status=500, safe=False)
        if 'password' not in data:
            return JsonResponse('password is required', status=500, safe=False)
        username = data['username']
        password = data['password']
        user = User.objects.filter(username=username)
        if user.first() is not None:
            if not user.first().is_active:
                return JsonResponse('user has not been activated', status=403, safe=False)
            auth_user = authenticate(username=username, password=password)
            if auth_user:
                    #return token
                    token = Token.objects.filter(user_id=auth_user.id)
                    if token:
                        return JsonResponse(str(token.first()), status=200, safe=False)
                    return JsonResponse('No token found', status=404, safe=False)
        else:
            return JsonResponse('No user found', status=404, safe=False)
