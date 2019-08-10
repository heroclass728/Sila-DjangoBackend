from django.shortcuts import render

# Create your views here.
# users/views.py
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

#drf
from rest_framework import generics
from . import models
from . import serializers

#signals
from allauth.account.signals import user_signed_up, password_set
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail


from .forms import CustomUserCreationForm

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'
    
#drf    
class UserListView(generics.ListCreateAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer


#send mail
@receiver(user_signed_up)
def employeeID(sender, **kwargs):
    # username = kwargs['request'].user.username
    email = kwargs['user'].email
    send_mail('Subject here','Here is the message.','accounts@drsila.com',[email],fail_silently=False,)
