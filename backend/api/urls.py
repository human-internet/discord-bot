from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRedirect, name='redirect'),
    path('start/', views.verifyAttempt, name='start'),
    path('success/', views.success, name='success'),
    path('confirm/', views.closeVerify, name='confirmation'),
    path('verification_successful/', views.verification_successful, name='suc'),
    path('fail/', views.fail, name='fail'),
]
