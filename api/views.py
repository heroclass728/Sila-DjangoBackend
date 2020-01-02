from django.shortcuts import render
from rest_framework.permissions import IsAuthenticated,AllowAny
# Create your views here.
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
# from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.twitter.views import TwitterOAuthAdapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from rest_auth.registration.views import SocialConnectView
from rest_auth.social_serializers import TwitterConnectSerializer

# from allauth.socialaccount.providers.oauth2.client import OAuth2Client



class FacebookConnect(SocialConnectView):
    permission_classes = [AllowAny]
    # def post(self,request):
    #     return "tests"
    adapter_class = FacebookOAuth2Adapter

class GoogleConnect(SocialConnectView):
    permission_classes = [AllowAny]
    client_class = OAuth2Client
    callback_url = 'https://api.drsila.com/api/accounts/google/login/callback/'
    adapter_class = GoogleOAuth2Adapter

class TwitterConnect(SocialConnectView):
    permission_classes = [AllowAny]
    serializer_class = TwitterConnectSerializer
    adapter_class = TwitterOAuthAdapter

# class GithubConnect(SocialConnectView):
#     adapter_class = GitHubOAuth2Adapter
#     callback_url = CALLBACK_URL_YOU_SET_ON_GITHUB
#     client_class = OAuth2Client
