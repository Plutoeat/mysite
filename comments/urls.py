#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/21 14:14
# @Author  : Joker
# @File    : urls.py
# @Software: PyCharm
from django.urls import path
from comments import views


app_name = "comments"
urlpatterns = [
    path('article/<int:article_id>/postcomment', views.CommentPostView.as_view(), name='postcomment'),
]
