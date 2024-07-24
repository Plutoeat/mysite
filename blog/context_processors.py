#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/9 16:35
# @Author  : Joker
# @File    : context_processors.py
# @Software: PyCharm
import logging

from django.utils import timezone

from blog.models import Category, Tag
from utils.common import cache, get_blog_setting

logger = logging.getLogger(__name__)


def seo_processor(requests):
    """
    常用的 SEO 词, context 全局
    :param requests: 请求
    :return: SEO 字典
    """
    key = 'seo_processor'
    value = cache.get(key)
    if value:
        return value
    else:
        logger.info('set processor cache.')
        setting = get_blog_setting()
        value = {
            'SITE_NAME': setting.site_name,
            'SHOW_GOOGLE_ADSENSE': setting.show_google_adsense,
            'GOOGLE_ADSENSE_CODES': setting.google_adsense_codes,
            'SITE_SEO_DESCRIPTION': setting.site_seo_description,
            'SITE_DESCRIPTION': setting.site_description,
            'SITE_KEYWORDS': setting.site_keywords,
            'SITE_BASE_URL': requests.scheme + '://' + requests.get_host() + '/',
            'ARTICLE_SUB_LENGTH': setting.article_sub_length,
            'category_list': Category.objects.all(),
            'tag_list': Tag.objects.all(),
            'OPEN_SITE_COMMENT': setting.open_site_comment,
            'RECORD_CODE': setting.record_code,
            'ANALYTICS_CODE': setting.analytics_code,
            "POLICE_RECORD_CODE": setting.police_record_code,
            "SHOW_POLICE_CODE": setting.show_police_code,
            "CURRENT_YEAR": timezone.now().year,
            "GLOBAL_HEADER": setting.global_header,
            "GLOBAL_FOOTER": setting.global_footer,
            "COMMENT_NEED_REVIEW": setting.comment_need_review,
        }
        cache.set(key, value, 60 * 60 * 10)
        return value
