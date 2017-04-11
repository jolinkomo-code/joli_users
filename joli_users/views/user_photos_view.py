from rest_framework.views import APIView
from django.http import HttpResponse, JsonResponse
from ..serializers.user_photo_serializer import UserPhotoSerializer
from rest_framework.parsers import FormParser, MultiPartParser,FileUploadParser
from django.forms.models import model_to_dict
from rest_framework.parsers import JSONParser
from django.core.files.base import ContentFile
import base64
from ..models.user_photos import UserPhotos
from ..models.user_profile import UserProfile
from django.core.mail import send_mail
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.core.mail import EmailMessage
from django.forms.models import model_to_dict
from django.conf import settings
import os

class UserPhotosView(APIView):
    parser_classes = (MultiPartParser, FileUploadParser)

    def put(self, request, format=None):
        data = JSONParser().parse(request)
        if 'image' not in data:
            return JsonResponse('image not found', status=500, safe=False)
        if 'user_profile' not in data:
            return JsonResponse('users user profile Id required', status=500, safe=False)
        if 'name' not in data:
            return JsonResponse('image name is required', status=500, safe=False)
        try:
            image = self.convert_image_from_mobile_upload(data['image'],data['user_profile'], data['name'])
            user_photos = UserPhotos.objects.filter(user_profile_id=data['user_profile'])
            if user_photos:
                user_photos = user_photos.first()
                user_photos.image = image
                user_photos.name = data['name']
            else:
                user_photos = UserPhotos(image=image, name=data['name'], user_profile_id=data['user_profile'])

            #delete already existing photos before saving
            format, imgstr = data['image'].split(';base64,')
            ext = format.split('/')[-1]
            #normal size
            self.delete_existing_image(settings.BASE_DIR + settings.JOLI_USER_PHOTOS_PATH + '/' +
            data['name'] + '_' + data['user_profile'] + '.' + ext)
            #user created thumbnails
            for thumbnail in settings.JOLI_USERS_IMAGE_THUMBNAILS:
                #format tuple to string
                thumbnail = str(thumbnail).replace('(','').replace(')','').replace(',','x').replace(' ','')
                self.delete_existing_image(settings.BASE_DIR + settings.JOLI_USER_PHOTOS_PATH + '/' +
                data['name'] + '_' + data['user_profile'] + '.' + thumbnail + '.' + ext)

            user_photos.save()
            return JsonResponse(True, status=200, safe=False)
        except Exception as e:
            print(e)
            return JsonResponse(model_to_dict(e), status=500)

    def convert_image_from_mobile_upload(self, data, user_profile_id, name):
        if isinstance(data, basestring) and data.startswith('data:image'):
            # base64 encoded image - decode
            format, imgstr = data.split(';base64,')  # format ~= data:image/X,
            ext = format.split('/')[-1]  # guess file extension

            data = ContentFile(base64.b64decode(imgstr), name=name + '_' + user_profile_id + '.' + ext)

        return data

    def delete_existing_image(self, path):
        """ param <path> could either be relative or absolute. """
        if os.path.isfile(path):
            os.remove(path)  # remove the file
        elif os.path.isdir(path):
            shutil.rmtree(path)  # remove dir and all contains
        else:
            print("file {} is not a file or dir.".format(path))
