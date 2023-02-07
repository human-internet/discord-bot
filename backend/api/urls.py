from django.urls import path
from . import views

urlpatterns = [
    path('', views.getRedirect, name='redirect'),
    path('start/', views.verifyAttempt, name='start'),
    path('fin/', views.finish, name='fin'),
    path('confirm/', views.closeVerify, name='confirmation'),
]
