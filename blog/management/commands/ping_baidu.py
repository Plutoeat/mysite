#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/18 23:11
# @Author  : Joker
# @File    : ping_baidu.py
# @Software: PyCharm
from django.core.management.base import BaseCommand

from blog.models import Article, Tag, Category
from utils.common import get_current_site
from utils.spider_notify import SpiderNotify

site = get_current_site().domain


class Command(BaseCommand):
    help = 'notify baidu url'

    def add_arguments(self, parser):
        parser.add_argument(
            'data_type',
            type=str,
            choices=[
                'all',
                'article',
                'tag',
                'category'],
            help='article : all article,tag : all tag,category: all category,all: All of these')

    def get_full_url(self, path):
        url = "https://{site}{path}".format(site=site, path=path)
        return url

    def handle(self, *args, **options):
        type = options['data_type']
        self.stdout.write('start get %s' % type)

        urls = []
        if type == 'article' or type == 'all':
            for article in Article.objects.filter(status='publish'):
                urls.append(article.get_full_url())
        if type == 'tag' or type == 'all':
            for tag in Tag.objects.all():
                url = tag.get_absolute_url()
                urls.append(self.get_full_url(url))
        if type == 'category' or type == 'all':
            for category in Category.objects.all():
                url = category.get_absolute_url()
                urls.append(self.get_full_url(url))

        self.stdout.write(
            self.style.SUCCESS(
                'start notify %d urls' %
                len(urls)))
        SpiderNotify.baidu_notify(urls)
        self.stdout.write(self.style.SUCCESS('finish notify'))
