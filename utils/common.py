#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 23:00
# @Author  : Joker
# @File    : common.py
# @Software: PyCharm
import functools
import logging
from hashlib import sha256

import markdown
from django.contrib.sites.models import Site
from django.core.cache import cache
from markdown.extensions.smarty import SmartyExtension
from markdown_extensions.emoji.extension import EmojiExtension
from markdown_katex.extension import KatexExtension

from utils.extensions import *

logger = logging.getLogger(__name__)


def get_blog_setting():
    """
    获取博客网站的设置
    """
    # 先从缓存中找
    # 如果存在直接返回
    # 如果不存在从数据库中获取，如数据库中没有, 则新增一个标准配置
    # 缓存并返回数据
    value = cache.get('x_blog_setting')
    if value:
        return value
    else:
        from blog.models import BlogSettings
        if not BlogSettings.objects.count():
            setting = BlogSettings()
            setting.site_name = 'XBlog'
            setting.site_description = '自用基于Django开发的博客系统'
            setting.site_seo_description = '自用基于Django开发的博客系统'
            setting.site_keywords = 'Django,Python'
            setting.article_sub_length = 300
            setting.hot_article_count = 7
            setting.comment_article_count = 8
            setting.show_google_adsense = False
            setting.open_site_comment = True
            setting.analytics_code = ''
            setting.record_code = ''
            setting.show_police_code = False
            setting.comment_need_review = False
            setting.save()
        value = BlogSettings.objects.first()
        logger.info('set cache x_blog_setting')
        cache.set('x_blog_setting', value)
        return value


def get_sha256(string: str) -> str:
    """
    将输入字符串通过 UTF-8 编码字节后通过哈希 256 算法加密, 最后将哈希值以 16 进制字符串形式返回
    :params string 输入字符串
    :return string 输出字符串
    """
    m = sha256(string.encode('utf-8'))
    return m.hexdigest()


def cache_decorator(expiration=3 * 60):
    """
    缓存装饰器, 将函数结果缓存
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 获取对象的字符串表示
            unique_str = repr((func, args, kwargs))
            # key 为对象字符串表示哈希 256 加密后的 16 进制字符串
            key = get_sha256(unique_str)
            value = cache.get(key)
            if value is not None:
                if str(value) == '__default_cache_value__':
                    return None
                else:
                    return value
            else:
                logger.debug('cache_decorator set cache:%s key:%s' % (func.__name__, key))
                value = func(*args, **kwargs)
                if value is None:
                    cache.set(key, '__default_cache_value__', expiration)
                else:
                    cache.set(key, value, expiration)
                return value
        return wrapper
    return decorator


@cache_decorator()
def get_current_site():
    """
    根据站点框架获取当前网站
    """
    site = Site.objects.get_current()
    return site


class CommonMarkdown:
    """
    通用 markdown 类, 用于处理 markdown 内容
    """
    @staticmethod
    def _convert_markdown(value):
        md = markdown.Markdown(
            extensions=[
                CustomTocExtension(),
                CommonExtension(),
                ListExtension(),
                DelExtension(),
                HighlightExtension(),
                FoldExtension(),
                ImageExtension(),
                'markdown.extensions.extra',
                'markdown.extensions.tables',
                'markdown.extensions.codehilite',
                'markdown.extensions.admonition',
                CustomFootNoteExtension(),
                EmojiExtension(),
                SmartyExtension(),
                KatexExtension(),
                IconExtension(),
                TableExtension(),
                AlertExtension()
            ]
        )
        body = md.convert(value)
        toc = md.toc
        return body, toc

    @staticmethod
    def get_markdown_with_all(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body, toc

    @staticmethod
    def get_markdown(value):
        body, toc = CommonMarkdown._convert_markdown(value)
        return body


def send_email(subject: str, message: str, recipient_list: list):
    """
    发送发送邮件的信号
    :param subject: 主题
    :param message: 信息
    :param recipient_list: 接收人列表
    """
    from signals.common import send_email_signal
    send_email_signal.send(
        send_email.__class__,
        subject=subject,
        message=message,
        recipient_list=recipient_list
    )


def expire_view_cache(path, servername, port, key_prefix=None):
    """
    刷新视图缓存
    :param path:url路径
    :param servername:host
    :param port:端口
    :param key_prefix:前缀
    :return:是否成功
    """
    from django.http import HttpRequest
    from django.utils.cache import get_cache_key

    request = HttpRequest()
    request.META = {'SERVER_NAME': servername, 'SERVER_PORT': port}
    request.path = path

    key = get_cache_key(request, key_prefix=key_prefix, cache=cache)
    if key:
        logger.info('expire_view_cache:get key:{path}'.format(path=path))
        if cache.get(key):
            cache.delete(key)
        return True
    return False


def delete_view_cache(prefix, keys):
    from django.core.cache.utils import make_template_fragment_key
    key = make_template_fragment_key(prefix, keys)
    cache.delete(key)
