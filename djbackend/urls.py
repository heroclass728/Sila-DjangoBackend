"""djbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from django_ses.views import handle_bounce
from django.views.decorators.csrf import csrf_exempt


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('accounts/', include('allauth.urls')),
    path('users/', include('users.urls')), # new user app with custom model
    path('users/', include('django.contrib.auth.urls')),
    path('pages/', include('pages.urls')),
    path('ses/bounce/', csrf_exempt(handle_bounce)),
    path('admin/django-ses/',include('django_ses.urls')),
    path('tinymce/', include('tinymce.urls')),
]


admin.site.site_header = "Dr.Sila"
admin.site.site_title = "Dcatra"
admin.site.index_title = "Dr.sila App Admin"
