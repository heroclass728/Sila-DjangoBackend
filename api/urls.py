from django.contrib import admin
from django.urls import path,include
from api.views import FacebookConnect,TwitterConnect
from users import views
urlpatterns = [
#     path('admin/', admin.site.urls),
    path('rest-auth/facebook/connect/', FacebookConnect.as_view(), name='fb_connect'),
    path('rest-auth/twitter/connect/', TwitterConnect.as_view(), name='twitter_connect'),
    path('rest-auth/', include('rest_auth.urls')),
    path('neo/', include('neo.urls')),
    path('rest-auth/registration/', include('rest_auth.registration.urls')),
    path('activate_user/', views.useractivate),
    path('resend_activation/', views.resend_activation),
    path('emailcheck/', views.emailcheck)
#     path('rest-auth/github/connect/$', GithubConnect.as_view(), name='github_connect')
]
