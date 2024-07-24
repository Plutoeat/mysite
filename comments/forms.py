#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/4 22:23
# @Author  : Joker
# @File    : forms.py
# @Software: PyCharm
from django import forms
from django.forms import ModelForm

from comments.models import Comment


class CommentForm(ModelForm):
    """
    评论表单
    """
    parent_comment_id = forms.IntegerField(widget=forms.HiddenInput, required=False)

    class Meta:
        model = Comment
        fields = ['body']
