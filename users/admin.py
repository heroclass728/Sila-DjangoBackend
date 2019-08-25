# from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .models import custom_verification_code as cvc
from .models import user_data
from . import models


class accountdatainline(admin.TabularInline):
    model = models.account_data
class userdatainline(admin.TabularInline):
    model = models.user_data
    extra=0
class transactionsinline(admin.TabularInline):
    model = models.transactions
    extra=0

class reportsinline(admin.TabularInline):
    model = models.reports
    extra=0

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    inlines = [accountdatainline,userdatainline,transactionsinline,reportsinline]


class subscrptionadmin(admin.ModelAdmin):
    list_display = ['name','price','allowed_reports','extension_days','allowed_subusers']
class cvcadmin(admin.ModelAdmin):
    list_display = ['email','code']
class userdataadmin(admin.ModelAdmin):
    list_display = ['account_type','name','dob','gender','report_count']
#class userdataadmin(admin.ModelAdmin):
#    list_display = ['user','name','age','gender','report_count']




admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(cvc,cvcadmin)
admin.site.register(models.subscription_plans,subscrptionadmin)
admin.site.register(user_data,userdataadmin)
admin.site.register(models.account_data)
admin.site.register(models.transactions)
admin.site.register(models.reports)
