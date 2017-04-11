from django.http import HttpResponse, JsonResponse
from rest_framework.parsers import JSONParser
from django.contrib.auth.models import User
from ..serializers.user_serializer import UserSerializer
from ..models.user_profile import UserProfile
from ..models.user_photos import UserPhotos
from rest_framework.views import APIView
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from django.forms.models import model_to_dict
from django.conf import settings
import datetime
import base64
import os

class UserView(APIView):

    def post(self, request, format=None):
        data = JSONParser().parse(request)
        #first check if username already exists
        if 'first_name' not in data:
            return JsonResponse('first name is a required field', status=200, safe=False)
        if 'last_name' not in data:
            return JsonResponse('last_name is a required field', status=200, safe=False)
        if 'username' not in data:
            return JsonResponse('username is a required field', status=200, safe=False)
        if 'password' not in data:
            return JsonResponse('password is a required field', status=200, safe=False)
        if 'email' not in data:
            return JsonResponse('email is a required field', status=200, safe=False)

        user_exists = User.objects.filter(username=data['username'])
        if user_exists:
            return JsonResponse('user already exists', status=200, safe=False)
        user_s = UserSerializer(data=data)

        #save new user
        if(user_s.is_valid()):
            user_s.save()
            saved_user = User.objects.get(pk=user_s.data['id'])
            if saved_user:
                #add user to user group
                try:
                    g = Group.objects.get(name=settings.JOLI_USERS_USER_GROUP_NAME)
                except Exception as e:
                    return JsonResponse(error='no user groups created', status=200)
                g.user_set.add(saved_user.id)

                #send user confirmation email
                token = Token.objects.filter(user_id=saved_user.id)
                if token:
                    token = token.first()
                    try:
                        verify_link = request.get_host() +  '/eventstaff/users/confirm_account/?verify_id=' + token
                        msg = EmailMessage(
                            settings.JOLI_USERS_EMAIL_SUBJECT,
                            'Hi ' + user.first_name + ' ' + user.last_name + ', <br><br> ' + JOLI_USERS_EMAIL_BODY_TEXT + '. Please follow this link ' + verify_link,
                            settings.JOLI_USERS_EMAIL_FROM,
                            [user.email],
                        )
                        msg.content_subtype = "html"
                        msg.send()
                    except Exception as e:
                        return JsonResponse(model_to_dict(e), status=200)

                    return JsonResponse(token, status=200, safe=False)
                else:
                    return JsonResponse('No user token created', status=200, safe=False)
            else:
                return JsonResponse('error saving user', status=200, safe=False)

        return JsonResponse('attempted to save an invalid user', status=200, safe=False)

    def get(self, request,format=None):
        if request.method == 'GET':
            #init, so if empty client wont throw a property undefined error when client tries to read an empty property
            user_profile_dict = {}
            user_profile_dict['user'] = {'first_name': '','last_name': '', 'email': ''}
            user_profile_dict['profile'] = {'gender':'', 'birth_date':'',
             'address': '', 'location':'', 'occupation':'', 'status':'',
              'mobile_no':'', 'interest':'',id: 0, 'user_id':0}
            user_profile_dict['user'] = {'first_name': request.user.first_name,'last_name': request.user.last_name, 'email': request.user.username }
            user_profile = UserProfile.objects.filter(user_id=request.user.id)
            if user_profile:
                user_profile_dict['profile'] = model_to_dict(user_profile.first())
                #get user profile photo if specified
                profile_photo_size = request.GET.get('profile_photo_size', '')
                if profile_photo_size is not '':
                    user_photo = UserPhotos.objects.filter(user_profile_id=user_profile.first().id)
                    if user_photo:
                        user_photo = user_photo.first()
                        #reconstruct saved profile pic
                        saved_photo_name = user_photo.name + '_' + str(user_photo.user_profile_id);
                        user_profile_dict['profile_photo'] = ''
                        user_profile_dict['profile_photo_url'] = ''
                        if profile_photo_size == 'original':
                                if os.path.isfile('/' + user_photo.image.url):
                                    with open('/' + user_photo.image.url, "rb") as image_file:
                                        encoded_photo_string = base64.b64encode(image_file.read())
                                    user_profile_dict['profile_photo'] = encoded_photo_string
                                    user_profile_dict['profile_photo_url'] = settings.HOST + settings.JOLI_USER_PHOTOS_RELATIVE_PATH + '/' + user_photo.name + '_' + str(user_photo.user_profile_id) + '.jpeg'
                        else:
                            if os.path.isfile('/' + getattr(user_photo.image, 'url_' + profile_photo_size)):
                                with open('/' + getattr(user_photo.image, 'url_' + profile_photo_size, "rb")) as image_file:
                                    encoded_photo_string = base64.b64encode(image_file.read())
                                user_profile_dict['profile_photo'] = encoded_photo_string
                                user_profile_dict['profile_photo_url'] = settings.HOST + settings.JOLI_USER_PHOTOS_RELATIVE_PATH + '/' + user_photo.name + '_' + str(user_photo.user_profile_id) + '.' + profile_photo_size + '.jpeg'
            return JsonResponse(user_profile_dict, status=200)

    def put(self, request, format=None):
        if request.method == 'PUT':
            data = JSONParser().parse(request)
            #update user
            saved_user = User.objects.get(pk=request.user.id)
            if 'first_name' in data and data['first_name'] is not '':
                saved_user.first_name = data['first_name']

            if 'last_name' in data and data['last_name'] is not '':
                saved_user.last_name = data['last_name']

            saved_user.save()
            if 'password' in data and data['password'] is not '':
                #update user password
                saved_user.set_password(data['password'])

            #update user profile
            self.save_user_profile(saved_user.id, data)
            return JsonResponse('user updated', status=200, safe=False)

    def save_user_profile(self, user_id, data):
        user_profile = UserProfile.objects.filter(user_id=user_id)
        if user_profile :
            user_profile = UserProfile.objects.filter(user_id=user_id).first()
        else:
            user_profile = UserProfile()
            user_profile.user_id = saved_user.id

        if 'gender' in data and data['gender'] is not '':
            user_profile.gender = data['gender']
        if 'birth_date' in data and data['birth_date'] is not '':
            try:
                datetime.datetime.strptime(data['birth_date'], '%d-%m-%Y')
            except ValueError:
                return JsonResponse('invalid date for birth date', status=200, safe=False)
            user_profile.birth_date = data['birth_date']

        if 'address' in data and data['address'] is not '':
            user_profile.address = data['address']

        if 'location' in data and data['location'] is not '':
            user_profile.location = data['location']

        if 'occupation' in data and data['occupation'] is not '':
            user_profile.occupation = data['occupation']

        if 'status' in data and data['status'] is not '':
            user_profile.status = data['status']

        if 'mobile_no' in data and data['mobile_no'] is not '':
            user_profile.mobile_no = data['mobile_no']

        if 'interest' in data and data['interest'] is not '':
            user_profile.interest = data['interest']

        user_profile.save()
