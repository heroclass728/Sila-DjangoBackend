from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.contrib.auth import get_user_model
# from django.db import models
from django.conf import settings
from datetime import datetime as dtm
import datetime

from ApiSettings import *


def getenddate():
    return (datetime.datetime.now() + datetime.timedelta(DEFAULT_DAYS)).date()

class CustomUser(AbstractUser):
    name = models.CharField(null=True,blank=True, max_length=255)
    pass

    def __str__(self):
        return self.email
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Call the "real" save() method
        if not account_data.objects.filter(user=self).count():
            f = account_data(user=self)
            f.save()

class usocial(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,unique=True)
    provider = models.CharField(max_length=50,blank=False,null=False)
    uid = models.CharField(max_length=500,blank=False,null=False)
    def __str__(self):
        return self.user.email



class account_data(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,unique=True)
    report_count = models.IntegerField(null=False,default=0)
    startdate = models.DateField(default=date.today)
    enddate = models.DateField(default=getenddate())
    date_check = models.BooleanField(default=DATE_CHECK)
    reports_allowed = models.IntegerField(null=False,default=DEFAULT_REPORTS)
    plan_reports = models.IntegerField(null=False,blank=False,default=DEFAULT_REPORTS)
    report_check = models.BooleanField(default=REPORTS_CHECK)
    subusers_allowed = models.IntegerField(null=False,default=DEFAULT_SUBUSERS)
    plan_subusers = models.IntegerField(null=False,blank=False,default=DEFAULT_SUBUSERS)
    subuser_check = models.BooleanField(default=SUB_USER_CHECK)
    plan_name = models.CharField(max_length=40,null=False,unique=False,blank=False,default = 'Free')
    language = models.CharField(max_length=40,null=False,unique=False,blank=False,default = 'en')
    def __str__(self):
        return self.user.email



class custom_verification_code(models.Model):
    email = models.EmailField(max_length=70,blank=True, null= True, unique= True)
    code = models.IntegerField(null= False, unique= True)


class user_data(models.Model):
    account_type = models.IntegerField(null=False)
    name = models.CharField(max_length=40,null=False)
#    age = models.IntegerField(null=False,blank=True)
    dob = models.DateField(null=True,blank=True)
    email = models.EmailField(max_length=70,blank=True, null=True)
    gender = models.CharField(max_length=10,null=False,blank=False)
    pregnancy = models.BooleanField(null=False,blank=False)
    report_count = models.IntegerField(null=True,default=0)
    account_id = models.ForeignKey(CustomUser,on_delete=models.CASCADE) ###change to PROTECT
    active = models.BooleanField(null=False,default=True)
    relation = models.CharField(max_length=40,null=True,blank=True)
    def __str__(self):
        return self.name

class subscription_plans(models.Model):
    name = models.CharField(max_length=40,null=False,unique=True,blank=True)
    description = models.TextField()
    price = MoneyField(max_digits=14, decimal_places=2)
    allowed_reports = models.IntegerField(blank=False,null=False)
    infinate_reports = models.BooleanField(default=False)
    extension_days = models.IntegerField(blank=False,null=False,default = 30)
    infinate_days = models.BooleanField(default=False)
    allowed_subusers = models.IntegerField(blank=False,null=False,default = 5)
    infinate_subusers = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class transactions(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) ### change to PROTECT
    transaction_id = models.CharField(max_length=120,null=False,blank=False)
    payment_method = models.CharField(max_length=60,null=False,blank=False)
    coupon_used = models.CharField(max_length=60,null=True,blank=True)
#    date = models.DateTimeField(auto_now_add=True, blank=False)
    payment_datetime = models.DateTimeField(default=dtm.now,blank =False)
    amount_paid = models.IntegerField(blank=False,null=False)
    currency_paid = models.CharField(max_length=60,null=False,blank=False)
    plan = models.CharField(max_length = 30,null=True,blank=True)
    def __str__(self):
        return self.user.email


class reports(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) ######change to PROTECT
    profile = models.ForeignKey(user_data, on_delete=models.CASCADE)  ###change to PROTECT
    symptomps = models.CharField(max_length=500,blank=False,null=False)
    diseases = models.CharField(max_length=500,blank=False,null=False)
    date = models.DateTimeField(max_length=60,default=dtm.now,blank =False)
    danger_score = models.IntegerField(blank=False,null=False,default=0)
    common_score = models.IntegerField(blank=False,null=False,default=0)
    doctor = models.CharField(max_length=500,blank=True,null=True)

    def __str__(self):
        return self.profile.name
