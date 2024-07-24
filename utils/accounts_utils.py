#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/5/19 17:59
# @Author  : Joker
# @File    : accounts_utils.py
# @Software: PyCharm
import logging
import random
import string
import typing
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.urls import reverse

from accounts.models import OAuthConfig
from accounts.oauth_manager import BaseOAuthManager
from mysite import settings
from utils.common import get_current_site, send_email, get_sha256, cache, cache_decorator

logger = logging.getLogger(__name__)


def set_user_status(form) -> settings.AUTH_USER_MODEL:
    """
    设置 User 状态为不活跃，并将来源定义未普通注册, 仅用于通过 RegisterForm 注册的用户
    :param form: RegisterForm
    :return: User
    """
    user = form.save(False)
    user.is_active = False
    user.source = "Register"
    user.save(True)
    return user


def get_verify_url(user: settings.AUTH_USER_MODEL) -> str:
    """
    生成一个验证邮箱链接
    :param user: User 用户
    :return: str 验证邮件链接
    """
    site = get_current_site().domain
    path = reverse("accounts:result")
    token = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
    scheme = 'https'
    if settings.DEBUG:
        scheme = 'http'
    url = f"{scheme}://{site}{path}?type=validation&id={user.id}&token={token}"
    return url


def send_verify_email(url: str, user: settings.AUTH_USER_MODEL) -> None:
    """
    发送一个验证邮件
    :param url: 验证链接
    :param user: 接受人
    :return:
    """
    msg = """
        <p>请点击下面链接验证您的邮箱</p>

        <a href="{url}" rel="bookmark">点此验证</a>

        <br />
        如果上面链接无法打开，请将此链接复制至浏览器。
        {url}
    """.format(url=url)

    send_email(
        subject="验证您的电子邮箱",
        message=msg,
        recipient_list=[user.email, ]
    )


def verify_token(token: str, user: settings.AUTH_USER_MODEL) -> bool:
    """
    验证token是否正确
    :param token: 从链接上获取的token
    :param user: 根据id获取到的user
    :return: 验证结果
    """
    c_sign = get_sha256(get_sha256(settings.SECRET_KEY + str(user.id)))
    return c_sign == token


def generate_code() -> str:
    """生成随机数验证码"""
    return ''.join(random.sample(string.digits, 6))


def send_reset_email(to_mail: str, code: str, subject: str = "邮件验证码"):
    """发送重设密码验证码
    Args:
        to_mail: 接受邮箱
        subject: 邮件主题
        code: 验证码
    """
    html_content = f"您正在重设密码，验证码为：{code}, 5分钟内有效，请妥善保管"
    send_email(subject=subject, message=html_content, recipient_list=[to_mail])


def verify(email: str, code: str):
    """验证code是否有效
    Args:
        email: 请求邮箱
        code: 验证码
    """
    cache_code = get_code(email)
    if cache_code != code:
        raise ValidationError("验证码错误！")


_code_ttl = timedelta(minutes=5)


def set_code(email: str, code: str):
    """设置code"""
    cache.set(email, code, _code_ttl.seconds)


def get_code(email: str) -> typing.Optional[str]:
    """获取code"""
    return cache.get(email)


@cache_decorator(expiration=100 * 60)
def get_oauth_apps():
    """
    返回一个可使用的第三方列表
    """
    configs = OAuthConfig.objects.filter(is_enable=True).all()
    if not configs:
        return []
    config_apps = [config.oauth_app.code for config in configs]
    applications = BaseOAuthManager.__subclasses__()
    apps = [application() for application in applications if application().CODE in config_apps]
    return apps


def get_manager_by_app(app):
    """
    返回一个指定的 manager
    """
    applications = get_oauth_apps()
    if applications:
        finds = list(filter(
            lambda x: x.CODE == app,
            applications
        ))
        if finds:
            return finds[0]
    return None


def verify_oauth_app(request):
    """
    检验请求是否携带 oauth_app 查询参数, 指定 manager 是否存在, 均存在返回 manager
    """
    oauth_app = request.GET.get('oauth_app', None)
    if not oauth_app:
        return False
    manager = get_manager_by_app(oauth_app)
    if not manager:
        return False
    return manager


def get_oauth_redirect_url(request):
    """
    获取重定向链接
    """
    next_url = request.GET.get('next', None)
    if not next_url or next_url == '/login/':
        return '/profile/'
    return next_url


def send_oauth_verify_email(oauth_user):
    """
    发送 oauth 的验证邮箱
    :params oauth_user
    """
    token = get_sha256(get_sha256(settings.SECRET_KEY + str(oauth_user.id)))
    site = get_current_site().domain
    path = reverse('accounts:email_verification', kwargs={
        'oauth_id': oauth_user.id,
        'token': token
    })
    scheme = 'https'
    if settings.DEBUG:
        scheme = 'http'
    url = f"{scheme}://{site}{path}?type=validation&id={oauth_user.id}&token={token}"

    content = """
        <p>请点击下面链接绑定您的邮箱</p>

        <a href="{url}" rel="bookmark">{url}</a>

        再次感谢您！
        <br />
        如果上面链接无法打开，请将此链接复制至浏览器。
        {url}
    """.format(url=url)
    send_email(subject='绑定您的电子邮箱', message=content, recipient_list=[oauth_user.email])


def verify_oauth_token(token, oauth_id):
    """
    验证 oauth 的 token
    """
    c_sign = get_sha256(get_sha256(settings.SECRET_KEY + str(oauth_id)))
    return c_sign == token


def send_oauth_success_email(oauth_user):
    """
    发送 oauth 邮箱认证成功邮件
    :params oauth_user
    """
    scheme = 'https'
    if settings.DEBUG:
        scheme = 'http'
    site = get_current_site().domain
    content = '''
        <p>恭喜您，您已经成功绑定您的邮箱，您可以使用{oauth_app}来直接免密码登录本网站.欢迎您继续关注本站，地址是</p>

        <a href="{url}" rel="bookmark">{url}</a>

        再次感谢您！
        <br />
        如果上面链接无法打开，请将此链接复制至浏览器。
        {url}
    '''.format(oauth_app=oauth_user.oauth_app.app_name, url=f'{scheme}://{site}')

    send_email(subject='恭喜您绑定成功!', message=content, recipient_list=[oauth_user.email])
