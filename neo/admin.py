from django.contrib import admin

# Register your models here.
from . import models


class symptomadmin(admin.ModelAdmin):
    list_display = ['name','ar_name','synonyms','ar_synonyns']
class diseaseadmin(admin.ModelAdmin):
    list_display = ['name','ar_name','has']
class useradmin(admin.ModelAdmin):
    list_display = ['name','group','gender','pregnancy']
class doctoradmin(admin.ModelAdmin):
    list_display = ['name','ar_name','covers']


#admin.site.register(models.Symptom, symptomadmin)
#admin.site.register(models.Disease,diseseadmin)
#admin.site.register(models.User,useradmin)
#admin.site.register(models.Doctor,doctoradmin)
