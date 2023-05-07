from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRedirect, name='redirect'),
    path('start/', views.verifyAttempt, name='start'),
    path('confirm/', views.checkVerify, name='confirmation'),
    path('removeEntry/', views.closeVerify, name='close'),
    path('verification_successful/', views.verification_successful, name='suc'),
]
