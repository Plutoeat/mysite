#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/23 22:00
# @Author  : Joker
# @File    : sitemap.py
# @Software: PyCharm
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from blog.models import Article, Category, Tag


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = 'daily'

    def items(self):
        return ['blog:home', ]

    def location(self, item):
        return reverse(item)


class ArticleSiteMap(Sitemap):
    priority = "0.6"
    changefreq = "monthly"

    def items(self):
        return Article.objects.filter(status='publish')

    def lastmod(self, obj):
        return obj.last_mod_time


class CategorySiteMap(Sitemap):
    priority = "0.6"
    changefreq = "weekly"

    def items(self):
        return Category.objects.all()

    def lastmod(self, obj):
        return obj.last_mod_time


class TagSiteMap(Sitemap):
    changefreq = "weekly"
    priority = "0.3"

    def items(self):
        return Tag.objects.all()

    def lastmod(self, obj):
        return obj.last_mod_time


class UserSiteMap(Sitemap):
    priority = "0.3"
    changefreq = "weekly"

    def items(self):
        return list(set(map(lambda x: x.author, Article.objects.all())))

    def lastmod(self, obj):
        return obj.date_joined