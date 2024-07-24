#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/23 23:18
# @Author  : Joker
# @File    : build_index.py
# @Software: PyCharm
from django.core.management.base import BaseCommand

from backends.documents import ElapsedTimeDocument, ArticleDocumentManager, ElapsedTimeDocumentManager, \
    ELASTICSEARCH_ENABLED


class Command(BaseCommand):
    help = 'build search index'

    def handle(self, *args, **options):
        if ELASTICSEARCH_ENABLED:
            ElapsedTimeDocumentManager.build_index()
            manager = ElapsedTimeDocument()
            manager.init()
            manager = ArticleDocumentManager()
            manager.delete_index()
            manager.rebuild()
