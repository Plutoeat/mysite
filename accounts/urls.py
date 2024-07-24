#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/19 1:05
# @Author  : Joker
# @File    : urls.py
# @Software: PyCharm
from django.urls import path, include

from accounts import views


extra_urlpatterns = [
    path('login/', views.oauth_login, name='oauth_login'),
    path('authorize/', views.authorize, name='authorize'),
    path('require_email/<int:oauth_id>/', views.RequireEmailView.as_view(), name='require_email'),
    path('bind_success/<int:oauth_id>/', views.bind_success, name='bind_success'),
    path('email_verification/<int:oauth_id>/<str:token>/', views.email_verification, name='email_verification')
]

app_name = 'accounts'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.SignInView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('result/', views.account_result, name='result'),
    path('forget_password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('forget_password_code/', views.ForgetPasswordEmailCode.as_view(), name='forget_password_code'),
    path('oauth/', include(extra_urlpatterns)),
    path('profile/', views.user_profile, name='profile'),
]
