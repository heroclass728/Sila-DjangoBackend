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
from users.models import user_data,profile_data

#email
from django.template.loader import render_to_string
from django.utils.html import strip_tags



from .forms import CustomUserCreationForm
from django.http import JsonResponse


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
    username = kwargs['user'].username
    code = randint(100000, 999999)
    while cvc.objects.filter(code=code).exists():
        code = code + 1
    record = cvc(email=email,code=code)
    rr = user.objects.get(email=email)
    rr.is_active = False
    record.save()
    rr.save()
    content = 'Thanks for signing up for Dr. sila Please enter the following code to complete the signup process'
    html_message = render_to_string('email_template_en.html', {'code': code,'content':content,'username':username})
    plain_message = strip_tags(html_message)
    send_mail('Dr.Sila Verification code - {}'.format(code),plain_message,'accounts@drsila.com',[email],html_message=html_message,fail_silently=False)
    return
#class verify


def useractivate(request):
    try:
        code = request.GET['code']
        email = request.GET['email']
    except:
        return JsonResponse({"message":"Required Details are not provided"}, status=403)
    try:
        scode =  cvc.objects.get(email=email)
    except:
        if user.objects.filter(email=email).count():
            if user.objects.get(email=email).is_active:
                return JsonResponse({"message":"Email aready activated"}, status=403)
            else:
                return JsonResponse({"message":"Unable find the user"}, status=403)
        else:
            return JsonResponse({"message":"Email not registered "}, status=403)

    if str(code) == str(scode.code):
        scode.delete()
        rr = user.objects.get(email=email)
        rr.is_active = True
        rr.save()
        return JsonResponse({"message":"user activated"})
    else:
        return JsonResponse({"message":"Code incorrect"}, status=403)

def resend_activation(request):
    try:
        email = request.GET['email']
    except:
        return JsonResponse({"message":"Required Details are not provided"}, status=403)
    if not user.objects.filter(email=email).count():
        return  JsonResponse({"message":"email is not yet registered"}, status=403)
    rr = user.objects.get(email=email)
    if rr.is_active:
        return  JsonResponse({"message":"User is already activated"}, status=403)
    if not  cvc.objects.filter(email=email).count():
        return  JsonResponse({"message":"code not found in the database, please contact support"}, status=403) 

    scode = cvc.objects.get(email=email)
    username = rr.username
    code = scode.code
    try:
        content = 'Thanks for signing up for Dr. sila Please enter the following code to complete the signup process'
        html_message = render_to_string('email_template_en.html', {'code': code,'content':content,'username':username})
        plain_message = strip_tags(html_message)
        send_mail('Dr.Sila Verification code - {}'.format(code),plain_message,'accounts@drsila.com',[email],html_message=html_message,fail_silently=False)
        return JsonResponse({"message":"Verification code resent successfully"})
    except:
        return JsonResponse({"message":"Something Went wrong"}, status=403)
