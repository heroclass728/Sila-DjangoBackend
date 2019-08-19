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


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm


class subscrptionadmin(admin.ModelAdmin):
    list_display = ['name','price','report_count']
class cvcadmin(admin.ModelAdmin):
    list_display = ['email','code']
class userdataadmin(admin.ModelAdmin):
    list_display = ['account_type','name','age','gender','report_count']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(cvc,cvcadmin)
admin.site.register(models.subscriptions,subscrptionadmin)
admin.site.register(user_data,userdataadmin)

