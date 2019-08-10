from django.shortcuts import render
from django.http import HttpResponse
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
from users.models import custom_verification_code as cvc
from random import randint
from users.models import CustomUser as user


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
def send_code(sender, **kwargs):
    # username = kwargs['request'].user.username
    email = kwargs['user'].email
    code = randint(100000, 999999)
    while cvc.objects.filter(code=code).exists():
        code = code + 1
    record = cvc(email=email,code=code)
    rr = user.objects.get(email=email)
    rr.is_active = False
    record.save()
    rr.save()
    send_mail('Dr.Sila Verification code','Here is the code- {}.'.format(code),'accounts@drsila.com',[email],fail_silently=False)
    return
#class verify


def useractivate(request):
    try:
        code = request.GET['code']
        email = request.GET['email']
    except:
        return HttpResponse("Required Details are not provided")
    
    scode =  cvc.objects.get(email=email)
    if str(code) == str(scode.code):
        scode.delete()
        rr = user.objects.get(email=email)
        rr.is_active = True
        rr.save()
        return HttpResponse("user activated")
    else:
        return HttpResponse("Code incorrect")

def resend_activation(request):
    try:
        email = request.GET['email']
    except:
        return HttpResponse("Required Details are not provided")
    rr = user.objects.get(email=email)
    if rr.is_active:
        return  HttpResponse("User is already activated")
    if not  cvc.objects.filter(email='shop2local@gmail.com').count():
        return  HttpResponse("email is not yet registered") 

    scode =  cvc.objects.get(email=email)
    try:
        send_mail('Dr.Sila Verification code','Here is the code- {}.'.format(scode.code),'accounts@drsila.com',[email],fail_silently=False0)
        return HttpResponse("Verification code resent successfully")
    except:
        return HttpResponse("Something Went wrong")
