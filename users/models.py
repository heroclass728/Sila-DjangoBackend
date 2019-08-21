from django.db import models
from djmoney.models.fields import MoneyField
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
# from django.db import models
from django.conf import settings

class CustomUser(AbstractUser):
#    username = models.CharField(max_length=100, blank=False,unique=False,null=False)
#    subscription = models.ForeignKey(subscriptions,null=False,default=1)
#    report_count = models.IntegerField(null=False,default=0)
    pass

    def __str__(self):
        return self.email
    # add additional fields in here


class custom_verification_code(models.Model):
    email = models.EmailField(max_length=70,blank=True, null= True, unique= True)
    code = models.IntegerField(null= False, unique= True)


class user_data(models.Model):
    account_type = models.IntegerField(null=False)
    name = models.CharField(max_length=40,null=False)
    age = models.IntegerField(null=False,blank=False)
    email = models.EmailField(max_length=70,blank=True, null=True)
    gender = models.CharField(max_length=10,null=False,blank=False)
    pregnancy = models.BooleanField(null=False,blank=False)
    report_count = models.IntegerField(null=True,default=0)
    account_id = models.IntegerField(null=False,blank=False)
    active = models.BooleanField(null=False,default=True)
#class profile_data(models.Model):
#    account_key  = models.ForeignKey(CustomUser,on_delete=models.PROTECT)
#    subscription = models.IntegerField(default=0)
#    reports      = models.IntegerField(default=0)


class subscriptions(models.Model):
    name = models.CharField(max_length=40,null=False,unique=True,blank=True)
    description = models.TextField()
    price = MoneyField(max_digits=14, decimal_places=2)
    report_count = models.IntegerField(blank=False,null=False)
    active = models.BooleanField(default=True)
    def __str__(self):
        return self.name
