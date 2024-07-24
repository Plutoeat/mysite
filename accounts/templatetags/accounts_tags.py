#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/28 23:47
# @Author  : Joker
# @File    : accounts_tags.py
# @Software: PyCharm
import logging

from django import template
from django.http import HttpRequest
from django.urls import reverse

from utils.accounts_utils import get_oauth_apps
from utils.common import cache_decorator

logger = logging.getLogger(__name__)

register = template.Library()


def get_field(instance, field, default):
    """
    尝试获取某实例的某字段, 如没有获取则为默认值
    :param instance: 实例
    :param field: 字段
    :param default: 默认值
    :return: 字段值或者默认值
    """
    try:
        logger.info("instance {instance}, field {field}, default {default}".format(instance=instance, field=field, default=default))
        return eval('instance.{}'.format(field))
    except Exception as e:
        logger.warning("Exception: " + str(e))
        return default


@cache_decorator(60 * 60 *24)
@register.simple_tag
def load_user_avatar(user):
    """
    根据具体情况加载用户头像
    :param user: 用户
    :return: 用户头像链接
    """
    if get_field(user, 'profile_set', False) and get_field(user.profile_set, 'avatar', False):
        return user.profile_set.avatar.url
    elif get_field(user, 'oauthuser_set', False) and user.oauthuser_set.count() > 0:
        for oauth_user in user.oauthuser_set.all():
            if get_field(oauth_user, 'picture', False):
                return oauth_user.picture
    else:
        return "/static/base/image/cover.png"


@register.inclusion_tag('accounts/tags/oauth_apps.html')
def load_oauth_apps(request: HttpRequest) -> dict:
    """
    动态加载后台配置的可用 oauth app
    :param request: 用户请求 HttpRequest
    :return: 启用的 oauth app 字典
    """
    apps = get_oauth_apps()
    if apps:
        base_url = reverse('accounts:oauth_login')
        path = request.get_full_path()
        applications = list(map(lambda x: (x.CODE, x.NAME, f'{base_url}?oauth_app={x.CODE}&next={path}'), apps))
    else:
        applications = []
    return {'apps': applications}
