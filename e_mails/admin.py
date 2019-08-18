from django.contrib import admin

# Register your models here.
from . import models

admin.site.register(models.templates)
admin.site.register(models.content)
