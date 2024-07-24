#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/25 10:52
# @Author  : Joker
# @File    : create_test_data.py
# @Software: PyCharm
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management import BaseCommand

from blog.models import Category, Tag, Article, Links, LinkShowType, ExtraSection
from comments.models import Comment
from utils.common import get_current_site


class Command(BaseCommand):
    help = 'create test datas'

    def handle(self, *args, **options):
        user = get_user_model().objects.get_or_create(
            email='test@test.com', username='测试用户', password=make_password('123456'))[0]

        pcategory = Category.objects.get_or_create(
            name='我是父类目', parent_category=None)[0]

        category = Category.objects.get_or_create(
            name='子类目', parent_category=pcategory)[0]

        category.save()
        basetag = Tag()
        basetag.name = "标签"
        basetag.save()
        site = get_current_site()
        site.domain = 'localhost:8000'
        site.name = '博客应用'
        site.save()
        for i in range(1, 20):
            article = Article.objects.get_or_create(
                category=category,
                # cover='http://localhost:8000/static/base/image/cover.png',
                title='nice title ' + str(i),
                body='nice content ' + str(i),
                author=user)[0]
            tag = Tag()
            tag.name = "标签" + str(i)
            tag.save()
            article.tags.add(tag)
            article.tags.add(basetag)
            article.status = 'publish'
            article.save()
            link = Links()
            link.name = "友情链接" + str(i)
            link.link = "https://www.baidu.com/"
            link.master = "站长" + str(i)
            link.email = "test@test.com"
            link.desc = "友情链接描述" + str(i)
            link.icon = 'http://localhost:8000/static/base/image/logo-img.png'
            link.sequence = i
            link.show_type = LinkShowType.ALL
            link.save()
            extra_section = ExtraSection()
            extra_section.name = '额外区域' + str(i)
            extra_section.content = f"<a href='https://www.baidu/com/'>百度+{i}</a>"
            extra_section.sequence = i
            extra_section.is_enable = False
            extra_section.save()
            comment = Comment()
            comment.body = "评论内容" + str(i)
            comment.author = user
            comment.article = article
            comment.save()


        from utils.common import cache
        cache.clear()
        self.stdout.write(self.style.SUCCESS('created test datas \n'))