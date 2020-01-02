from rest_framework.views import APIView
from rest_framework import authentication, permissions
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
# users/views.py
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from random import randint
#drf
from rest_framework import generics
from . import models
from . import serializers
from users.models import usocial

#signals
from allauth.account.signals import user_signed_up, password_set
from allauth.socialaccount.signals import social_account_added,pre_social_login
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from users.models import custom_verification_code as cvc
from random import randint
from users.models import CustomUser as user
from users.models import user_data
from rest_framework import viewsets
from allauth.socialaccount.models import SocialAccount as socuser

from django.views.decorators.csrf import csrf_exempt


from django.contrib.auth.base_user import BaseUserManager as passgen
# email
from django.template.loader import render_to_string
from django.utils.html import strip_tags


from rest_framework.permissions import IsAuthenticated
from .forms import CustomUserCreationForm
from django.http import JsonResponse
import json

from rest_framework.authtoken.models import Token


from datetime import date,timedelta
#from django.core import serializers
#email app import
from e_mails.models import templates as etemplates
from django.template import Context, Template

class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

#drf
class UserListView(generics.ListCreateAPIView):
    queryset = models.CustomUser.objects.all()
    serializer_class = serializers.UserSerializer

class profile_data(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = models.user_data.objects.all()
    serializer_class = serializers.userdataser


class user_profile(APIView):
    authentication_classes = [authentication.TokenAuthentication]
#    permission_classes = [permissions.IsAdminUser]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        pid = request.GET.get("profile_id")
        if pid is not None:
            try:
                i = models.user_data.objects.get(id = pid,active=True)
            except:
                return JsonResponse({"message":"Invalid profile id"}, status=400)
            if i.account_id != user:
                return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
            type = ''
            if i.account_type==0:
                type = 'primary'
            if i.account_type==1:
                type = 'subuser'
            return JsonResponse({'profile':type,'id':i.id,'name':i.name,'dob':i.dob,'email':i.email,'gender':i.gender,'pregnancy':i.pregnancy,'relation':i.relation})

        profiles = models.user_data.objects.filter(account_id = user,active=True)
        plist = []
        for i in profiles:
            if i.account_type == 0:
                plist.append({'profile':'primary','id':i.id,'name':i.name,'dob':i.dob,'email':i.email,'gender':i.gender,'pregnancy':i.pregnancy,'relation':i.relation,'acount_id':user.id})
            else:
                plist.append({'profile':'subuser','id':i.id,'name':i.name,'dob':i.dob,'email':i.email,'gender':i.gender,'pregnancy':i.pregnancy,'relation':i.relation})
        return  JsonResponse(plist, safe=False)

    def post(self, request, format=None):
        user = request.user
        jdata =json.loads(request.body)
        if models.user_data.objects.filter(account_id=user,active=True).count() >= models.account_data.objects.get(user=user).subusers_allowed:
            return JsonResponse({"message":"Your limit of subusers has reached based on your plan"}, status=400)
        if not all(elm in list(jdata.keys()) for elm in ['name','dob','gender','pregnancy','primary']):
            return JsonResponse({"message":"Not all required variables are provided"}, status=400)
        accountdata = models.account_data.objects.get(user=user)
        # if accountdata.subuser_check:
        #     if not accountdata.subusers_allowed:
        #         JsonResponse({"message":"user cannot create more subusers, please renew the plan"}, status=400)
        if jdata['primary']==True: #not models.user_data.objects.filter(account_id=user.id).count():
            if models.user_data.objects.filter(account_id=user,account_type=0).count():
               return JsonResponse({"message":"user already has a primary profile"}, status=400)
            record = models.user_data.objects.create(account_type=0,name = jdata['name'],dob = jdata['dob'],gender = jdata['gender'],pregnancy = jdata['pregnancy'],account_id=user)
            record.email=user.email
            if 'relation' in jdata.keys():
                record.relation=jdata['relation']
            record.save()
            message = 'primary profile successfully created'
        else:
            record = models.user_data.objects.create(account_type=1,name = jdata['name'],dob = jdata['dob'],gender = jdata['gender'],pregnancy = jdata['pregnancy'],account_id=user)
            if 'email' in jdata.keys():
                record.email=jdata['email']
                record.save()
            if 'relation' in jdata.keys():
                record.relation=jdata['relation']
                record.save()
            message = 'subuser profile is successfully created'
        accountdata.subusers_allowed = accountdata.subusers_allowed - 1
        accountdata.save()
        return  JsonResponse({'message':message,'profile_id':record.id}, safe=False)

    def patch(self, request, format=None):
        user = request.user
        jdata =json.loads(request.body)
        pid = request.GET.get("profile_id")
        if pid is None:
            return JsonResponse({"message":"Profile id not provided"}, status=400)
        try:
            i = models.user_data.objects.get(id = pid)
        except:
            return JsonResponse({"message":"Invalid profile id"}, status=400)
        if i.account_id != user:
            return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
        if not all(elm in list(jdata.keys()) for elm in ['name','dob','gender','pregnancy']):
            return JsonResponse({"message":"Not all required variables are provided"}, status=400)
        i.name = jdata['name']
        i.dob = jdata['dob']
        i.gender = jdata['gender']
        i.pregnancy = jdata['pregnancy']
        if 'email' in jdata.keys():
            i.email = jdata['email']
        if 'relation' in jdata.keys():
            i.relation = jdata['relation']
        i.save()
        return  JsonResponse({"message":"Details updated successfully"})


    def delete(self, request, format=None):
        user = request.user
        pid = request.GET.get("profile_id")
        if pid is None:
            return JsonResponse({"message":"Profile id not provided"}, status=400)
        try:
            i = models.user_data.objects.get(id = pid)
        except:
            return JsonResponse({"message":"Invalid profile id"}, status=400)
        if i.account_id != user:
            return JsonResponse({"message":"Current user cannot access this profile"}, status=400)
        if i.account_type == 0:
            return JsonResponse({"message":"Primary profile cannot be deleted"}, status=400)
        i.active = False
        i.save()
        return JsonResponse({"message":"Successfully deleted the user profile"})

#email checkup
def emailcheck(request):
    try:
        email = request.GET['email']
    except:
        return JsonResponse({"message":"Required Details are not provided"}, status=400)
    if user.objects.filter(email=email).count():
        i = user.objects.get(email=email)
        return JsonResponse({"message":"Email is already registered","account_id":i.id}, status=403)
    else:
        return JsonResponse({"message":"Email is Not Registered"})
#    serializer_class = serializers.UserSerializer


#send mail
@receiver(user_signed_up)
def send_code(sender, **kwargs):
    # username = kwargs['request'].user.username
    email = kwargs['user'].email
    username = kwargs['user'].username
#    firstname = kwargs['user'].firtst
#    kkk = user.objects.get(email=email)
#    models.account_data.objects.create(user=kkk)

    rr = user.objects.get(email=email)
    # models.account_data.objects.create(user=rr)
    if socuser.objects.filter(user=rr).count():
        # return  JsonResponse({"message":"email is not yet registered"}, status=403)
        rr.is_active = True
    else:
        code = randint(100000, 999999)
        while cvc.objects.filter(code=code).exists():
            code = code + 1
        record = cvc(email=email,code=code)
        rr.is_active = False
        record.save()

        htmlstr = etemplates.objects.get(name='code_verification').temp
        htm_template = Template(htmlstr)
        content = 'Thanks for signing up for Dr. sila Please enter the following code to complete the signup process'
        context = Context({'code': code,'content':content,'username':username})
        html_message = htm_template.render(context)
        # etemplates.
        # htmlstr = etemplates.objects.get(name='code_verification').temp
        # html_message = render_to_string(htmlstr, {'code': code,'content':content,'username':username})
        plain_message = strip_tags(html_message)
        send_mail('Dr.Sila Verification code - {}'.format(code),plain_message,'accounts@drsila.com',[email],html_message=html_message,fail_silently=False)
    rr.save()
    return
#class verify


# @receiver(social_account_added)
# def makesocialac(sender, **kwargs):
#     email = kwargs['user'].email
#     # email = kwargs['email']
#     rr = user.objects.get(email=email)
#     models.account_data.objects.create(user=rr)
#     return



def updatename(request):
    try:
        name = request.GET['name']
        email = request.GET['email']
    except:
        return JsonResponse({"message":"Required Details are not provided"}, status=403)
    try:
        us =  user.objects.get(email=email)
    except:
        return JsonResponse({"message":"Email not registered "}, status=403)

    us.first_name = name
    try:
        ac.language = request.GET['language']
        ac = models.account_data.objects.get(user=us)
        ac.save()
    except:
        pass
    us.save()
    return JsonResponse({"message":"user first name updated successfully"})



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
        return JsonResponse({"message":"user activated","account_id":rr.id})
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



class coupon_redeem(APIView):
    authentication_classes = [authentication.TokenAuthentication]
#    permission_classes = [permissions.IsAdminUser]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        edit_profile = EditProfileForm(user=user)
        redeem = CouponForm()
        if request.method == 'POST':
            edit_profile = EditProfileForm(request.POST, user=user)
            redeem = CouponForm(request.POST, user=user)
            if redeem.is_valid():
                coupon = redeem.coupon
                coupon.redeem(request.user)
            else:
                pass
            return render(request, 'main/profile.html', {'edit_profile': edit_profile, 'redeem': redeem})

        return render(request, 'main/profile.html', {'edit_profile': edit_profile, 'redeem': redeem})

class plan_update(APIView):
#    authentication_classes = [authentication.TokenAuthentication]
#    permission_classes = [permissions.IsAdminUser]
#    permission_classes = [IsAuthenticated]
    def post(self, request):
        data = json.loads(request.body)
        if not all(elm in list(data.keys()) for elm in ['plan_id','user_id']):
            return JsonResponse({"message":"required details are not provided not provided"}, status=400)
        try:
            i = models.subscription_plans.objects.get(id = data['plan_id'])
        except:
            return JsonResponse({"message":"Invalid plan id"}, status=400)
        auser = user.objects.get(id=data['user_id'])
        adata = models.account_data.objects.get(user=auser)
        adata.reports_allowed =i.allowed_reports
        adata.report_check =i.infinate_reports
        adata.plan_reports =i.allowed_reports
        adata.subusers_allowed=i.allowed_subusers
        adata.subuser_check=i.infinate_subusers
        adata.plan_subusers=i.allowed_subusers
        adata.enddate = adata.enddate + timedelta(days=i.extension_days)
        adata.startdate = date.today
        adata.save()
        return JsonResponse({"message":"Plan updated successfully"})
    def get(self, request):
        data = models.subscription_plans.objects.filter(active=True)
        plans = []
        for i in data:
            plan = {}
            plan['days'] = None
            plan['reports_allowed'] = None
            plan['profiles_allowed'] = None
            plan['id'] = i.id
            if not i.infinate_reports:
                plan['reports_allowed']= i.allowed_reports
            if not i.infinate_days:
                plan['days'] = i.extension_days
            if not i.infinate_subusers:
                plan['profiles_allowed'] = i.allowed_subusers
            plan['description']=i.description
            plans.append(plan)
        return JsonResponse({"plans":plans})


def get_or_create_token(email):
    luser = user.objects.get(email=email)
    if not Token.objects.filter(user=luser):
        token = Token.objects.create(user=luser)
        ftoken = token.key
    else:
        ftoken = Token.objects.get(user=luser).key
    # print(token.key)
    return ftoken
def create_unique_username(email):
    username = email.split('@')[0]
    while (user.objects.filter(username=username).exists()):
        username= username+str(randint(0, 9))
    return username

@csrf_exempt
def usocialogin(request):
    if not request.method == "POST":
        return JsonResponse({"message":"Request should be POST"}, status=400)
    data = json.loads(request.body)
    if not all(elm in list(data.keys()) for elm in ['uid','provider']):
        return JsonResponse({"message":"required details are not provided not provided"}, status=400)
    if not usocial.objects.filter(uid=data['uid'],provider=data['provider']).exists():
        if 'email' not in data.keys():
            return JsonResponse({"message":"Email Required, no object found"}, status=200)
        else:
            if user.objects.filter(email=data['email']).exists():
                luser = user.objects.get(email=data['email'])
                newi = usocial(uid=data['uid'],provider=data['provider'],user=luser)
                newi.save()
                return JsonResponse({"token":get_or_create_token(data['email'])}, status=200)
            else:
                email = data['email']
                password = passgen().make_random_password()
                username = create_unique_username(email)
                cuser = user(username=username,email=email,password=password)
                cuser.save()
                newi = usocial(uid=data['uid'],provider=data['provider'],user=cuser)
                newi.save()
                return JsonResponse({"token":get_or_create_token(data['email'])}, status=200)
    else:
        k = usocial.objects.get(uid=data['uid'],provider=data['provider'])
        return JsonResponse({"token":get_or_create_token(k.user.email)}, status=200)

        # luser = user.objects.get(email=data['email'])
        # if luser == k:
        #     return JsonResponse({"token":get_or_create_token(data['email'])}, status=200)
        # else:
        #     return JsonResponse({"message":"Details did not match with the user")}, status=200)

    #         if user.objects.filter(email=data['email']).exists():
    #             luser = user.object.get(email=data['email'])
    #             return
    #     # return
    # if user.objects.filter(email=data['email']).exists():
    #     user = user.object.get(email=)
    #     # if models.usocial.filter(email=data['email'],).exists():
    #     #
    #     #     return
    #
    #     return
