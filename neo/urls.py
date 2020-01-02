from django.urls import include, path

from neo import views

urlpatterns = [
    path('symptoms/', views.getsyms.as_view()),
    path('userview/', views.userview.as_view()),
    path('qa/', views.qa.as_view()),
    path('symsearch/', views.symsearch1.as_view()),
    path('getsymptom/', views.getsymptom.as_view()),
    path('makesymsearch/', views.makesymsearch),
    path('report/', views.getreport.as_view()),
    path('getreport/', views.getreportsdata.as_view()),
]
