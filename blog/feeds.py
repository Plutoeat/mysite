#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/22 20:15
# @Author  : Joker
# @File    : feeds.py
# @Software: PyCharm
from django.contrib.auth import get_user_model
from django.contrib.syndication.views import Feed
from django.utils import timezone

from blog.models import Article
from utils.common import CommonMarkdown


class BlogFeed(Feed):
    """
    博客网站 feed
    """
    title = "X Blog"
    description = "自用基于Django开发的博客系统"
    link = "/feed/"

    def author_name(self):
        return get_user_model().objects.first().nickname

    def author_link(self):
        return get_user_model().objects.first().get_absolute_url()

    def items(self):
        return Article.objects.filter(status='publish').order_by('-created_time')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return CommonMarkdown.get_markdown(item.body)

    def item_link(self, item):
        return item.get_absolute_url()

    def feed_copyright(self):
        now = timezone.now()
        return "Copyright &copy; {year} XBlog".format(year=now.year)
