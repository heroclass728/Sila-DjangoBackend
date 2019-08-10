from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser
# from django.db import models

class CustomUser(AbstractUser):
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
    age = models.IntegerField(null=True)
    email = models.EmailField(max_length=70,blank=True, null=True, unique=True)
    gender = models.CharField(max_length=10,null=False)
    account_key = models.ForeignKey(CustomUser)

class profile_data(models.Model):
    account_key  = models.ForeignKey(CustomUser)
    subscription = models.IntegerField(default=0)
    reports      = models.IntegerField(default=0)
