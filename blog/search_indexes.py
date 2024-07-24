#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/23 21:56
# @Author  : Joker
# @File    : search_indexes.py
# @Software: PyCharm
from haystack import indexes

from blog.models import Article


class ArticleIndex(indexes.SearchIndex, indexes.Indexable):
    """
    文章索引
    """
    text = indexes.CharField(document=True, use_template=True)
    title = indexes.CharField(model_attr='title')
    body = indexes.CharField(model_attr='body')

    def get_model(self):
        return Article

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(status='publish').order_by('-article_order').order_by('-views').order_by('-created_time')
