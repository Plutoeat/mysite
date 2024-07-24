#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/17 21:49
# @Author  : Joker
# @File    : comments_tags.py
# @Software: PyCharm
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

from utils.common import CommonMarkdown

register = template.Library()


@register.filter()
@stringfilter
def comment_markdown(content):
    """
    评论markdown渲染器
    :param content: 内容
    :return: 渲染内容
    """
    content = CommonMarkdown.get_markdown(content)
    return mark_safe(content)
