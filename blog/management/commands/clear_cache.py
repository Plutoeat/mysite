#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/10 18:10
# @Author  : Joker
# @File    : clear_cache.py
# @Software: PyCharm
# @Description: 清理 cache
from django.core.management import BaseCommand

from utils.common import cache


class Command(BaseCommand):
    help = 'clear the whole cache'

    def handle(self, *args, **options):
        cache.clear()
        self.stdout.write(self.style.SUCCESS('Cleared cache\n'))
