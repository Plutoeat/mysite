#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/3/7 16:51
# @Author  : Joker
# @File    : filter.py
# @Software: PyCharm
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from blog.models import Article


class ArticleListFilter(admin.SimpleListFilter):
    """
    自定义文章后台过滤器
    """
    title = _("作者")
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = list(set(map(lambda x: x.author, Article.objects.all())))
        for author in authors:
            yield author.id, _(author.username)

    def queryset(self, request, queryset):
        author_id = self.value()
        if author_id:
            return queryset.filter(author__id__exact=author_id)
        else:
            return queryset
