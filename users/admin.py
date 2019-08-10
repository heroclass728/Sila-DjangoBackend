# from django.contrib import admin

# Register your models here.
# users/admin.py
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser
from .models import custom_verification_code as cvc


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(cvc)
