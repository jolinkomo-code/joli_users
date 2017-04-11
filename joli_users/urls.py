from django.conf.urls import url, include
from rest_framework.views import APIView
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework.authtoken import views
from views import user_view, user_profile_view,user_photos_view, authenticate_view

urlpatterns = [
    url(r'^users/$', user_view.UserView().as_view()),
    url(r'^users/authenticate/$', authenticate_view.Authenticate().as_view()),
    url(r'^users/user_profile/$', user_profile_view.UserProfileView.as_view()),
    url(r'^users/user_photos/$', user_photos_view.UserPhotosView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns, allowed=['json'])
