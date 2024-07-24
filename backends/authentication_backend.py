import re

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


def check_phone_number(phone_number: str) -> bool:
    """
    匹配字符串是否为电话号码
    :param phone_number: 电话号码
    :return:
    """
    # 正则表达式来源网络可能存在漏洞，应及时更新
    pattern = re.compile(r"^(13[0-9]|14[01456879]|15[0-35-9]|16[2567]|17[0-8]|18[0-9]|19[0-35-9])\d{8}$")
    res = pattern.match(phone_number)
    if res is not None:
        return True
    return False


def check_email(email: str) -> bool:
    """
    匹配字符串是否为邮箱
    :param email: 邮箱
    :return:
    """
    # 正则表达式来源网络可能存在漏洞，应及时更新
    pattern = re.compile(r"^([a-zA-Z\d][\w-]{2,})@(\w{2,})\.([a-z]{2,})(\.[a-z]{2,})?$")
    res = pattern.match(email)
    if res is not None:
        return True
    return False


class AuthModelBackend(ModelBackend):
    """
    允许用户使用手机号，邮箱，用户名登录, 在 settings.py 中配置 AUTHENTICATION_BACKENDS 生效
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        if check_email(username):
            kwargs = {"email": username}
        elif check_phone_number(username):
            kwargs = {'phone_number': username}
        else:
            kwargs = {'username': username}
        try:
            user = get_user_model().objects.get(**kwargs)
            if user.check_password(password):
                return user
        except get_user_model().DoesNotExist:
            return None

    def get_user(self, username):
        try:
            return get_user_model().objects.get(pk=username)
        except get_user_model().DoesNotExist:
            return None
