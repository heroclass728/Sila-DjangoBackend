from django.urls import include, path

from . import views

urlpatterns = [
    path('symptoms/', views.getsyms.as_view()),
    path('userview/', views.userview.as_view()),
    path('qa/', views.qa.as_view()),
    path('symsearch/', views.symsearch.as_view()),
]