#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 21:36
# @Author  : Joker
# @File    : forms.py
# @Software: PyCharm
from django import forms

from blog.models import Article, Links


class ArticleForm(forms.ModelForm):
    """
    文章表单
    """
    class Meta:
        model = Article
        fields = '__all__'


class LinksForm(forms.ModelForm):
    """
    友情链接表单
    """
    class Meta:
        model = Links
        fields = ['name', 'link', 'master', 'email', 'icon', 'desc', 'sequence', 'show_type']
