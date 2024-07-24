import json
import logging
import os
from abc import ABCMeta, abstractmethod
from urllib import parse

import requests
from django.db import models

from accounts.models import OAuthConfig, OAuthUser, OAuthApp
from accounts.oauth_exception import OAuthAccessTokenException

logger = logging.getLogger(__name__)


class BaseOAuthManager(models.Manager, metaclass=ABCMeta):
    """
    Base OAuth Manager
    """
    AUTH_URL = None
    TOKEN_URL = None
    API_URL = None
    CODE = None
    NAME = None

    def __init__(self, access_token=None, openid=None, refresh_token=None):
        super().__init__()
        self.access_token = access_token
        self.openid = openid
        self.refresh_token = refresh_token

    @property
    def is_authorized(self):
        """
        是否通过过验证
        :return:
        """
        return self.access_token is not None and self.openid is not None and self.refresh_token is not None

    @abstractmethod
    def get_authorization_url(self, next_url='/'):
        """
        获取认证链接
        :param next_url:
        :return:
        """
        pass

    @abstractmethod
    def get_access_token_by_code(self, code: str):
        """
        通过 code 获取 access_token
        :param code:
        :return:
        """
        pass

    @abstractmethod
    def refresh_access_token(self, refresh_token: str):
        """
        刷新 access_token
        :param refresh_token:
        :return:
        """
        pass

    @abstractmethod
    def get_oauth_userinfo(self):
        """
        获取用户基础信息
        :return:
        """
        pass

    @abstractmethod
    def clean_info_res_data(self, res) -> OAuthUser:
        """
        存储 oauth 用户
        :param res: 第三方应用响应
        :return:
        """
        pass

    def get_url(self, url, headers=None, params=None):
        res = requests.get(url=url, headers=headers, params=params)
        logger.info(res.text)
        return res.text

    def post_url(self, url, headers=None, params=None, data=None):
        res = requests.post(url=url, headers=headers, params=params, data=data)
        logger.info(res.text)
        return res.text

    def get_config(self):
        value = OAuthConfig.objects.filter(oauth_app__code=self.CODE)
        return value[0] if value else None


class GiteeOAuthManager(BaseOAuthManager):
    """
    Gitee OAuth Manager
    """
    AUTH_URL = 'https://gitee.com/oauth/authorize'
    TOKEN_URL = 'https://gitee.com/oauth/token'
    API_URL = 'https://gitee.com/api/v5/user'
    CODE = 'gitee'
    NAME = '码云'

    def __init__(self, access_token=None, openid=None, refresh_token=None):
        config = self.get_config()
        self.project_id = config.project_id if config else ''
        self.client_id = config.app_key if config else ''
        self.client_secret = config.app_secret if config else ''
        self.callback_url = config.callback_url if config else ''

        super().__init__(access_token, openid, refresh_token)

    def get_authorization_url(self, next_url='/'):
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.callback_url,
            'response_type': 'code',
            'scope': 'user_info emails'
        }
        url = self.AUTH_URL + "?" + parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code: str):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.callback_url
        }

        res = self.post_url(self.TOKEN_URL, params=params)

        obj = json.loads(res)

        if 'access_token' in obj:
            self.access_token = obj.get('access_token', None)
            self.refresh_token = obj.get('refresh_token', None)
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def refresh_access_token(self, refresh_token: str):
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        res = self.post_url(self.TOKEN_URL, params=data)

        obj = json.loads(res)

        if 'access_token' in obj:
            self.access_token = obj.get('access_token', None)
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def get_oauth_userinfo(self):
        params = {
            'access_token': self.access_token
        }
        res = self.get_url(self.API_URL, params=params)

        try:
            oauth_user = self.clean_info_res_data(res)
            return oauth_user
        except Exception as e:
            logger.error(e)
            logger.error('google oauth error res: ' + res)
            return None

    def clean_info_res_data(self, res) -> OAuthUser:
        datas = json.loads(res)
        oauth_user = OAuthUser()
        oauth_user.metadata = res
        oauth_user.picture = datas['avatar_url']
        oauth_user.nickname = datas['name']
        oauth_user.openid = datas['id']
        oauth_user.oauth_app = OAuthApp.objects.get(code='gitee')
        oauth_user.access_token = self.access_token
        if datas.get('email', False):
            oauth_user.email = datas['email']
        if self.refresh_token:
            oauth_user.refresh_token = self.refresh_token
        return oauth_user


class ProxyManagerMixin:
    """
    添加代理，针对部分网站无法访问
    """

    def __init__(self, *args, **kwargs):
        if os.environ.get("HTTP_PROXY"):
            self.proxies = {
                "http": os.environ.get("HTTP_PROXY"),
                "https": os.environ.get("HTTP_PROXY")
            }
        else:
            self.proxies = None

    def get_url(self, url, headers=None, params=None):
        res = requests.get(url=url, headers=headers, params=params, proxies=self.proxies)
        return res.text

    def post_url(self, url, headers=None, params=None, data=None):
        res = requests.post(url, headers=headers, params=params, data=data, proxies=self.proxies)
        return res.text


class GithubOAuthManager(ProxyManagerMixin, BaseOAuthManager):
    """
    GitHub OAuth Manager
    """
    AUTH_URL = 'https://github.com/login/oauth/authorize'
    TOKEN_URL = 'https://github.com/login/oauth/access_token'
    API_URL = 'https://api.github.com/user'
    CODE = 'github'
    NAME = 'Github'

    def __init__(self, access_token=None, openid=None, refresh_token=None):
        config = self.get_config()
        self.project_id = config.project_id if config else ''
        self.client_id = config.app_key if config else ''
        self.client_secret = config.app_secret if config else ''
        self.callback_url = config.callback_url if config else ''

        super().__init__(access_token, openid, refresh_token)

    def get_authorization_url(self, next_url='/'):
        params = {'client_id': self.client_id}
        url = self.AUTH_URL + "?" + parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code: str):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
        }
        res = self.post_url(self.TOKEN_URL, params=params)
        obj = parse.parse_qs(res)
        if 'access_token' in obj:
            self.access_token = obj.get('access_token', [None])[0]
            self.refresh_token = obj.get('refresh_token', [None])[0]
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def refresh_access_token(self, refresh_token: str):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        res = self.post_url(self.TOKEN_URL, params=params)
        obj = parse.parse_qs(res)
        if 'access_token' in obj:
            self.access_token = obj.get('access_token', [None])[0]
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def get_oauth_userinfo(self):
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': 'Bearer {}'.format(self.access_token),
            'X-GitHub-Api-Version': '2022-11-28'
        }
        res = self.get_url(self.API_URL, headers=headers)
        try:
            oauth_user = self.clean_info_res_data(res)
            return oauth_user
        except Exception as e:
            logger.error(e)
            logger.error('github oauth error res: ' + res)
            return None

    def clean_info_res_data(self, res) -> OAuthUser:
        datas = json.loads(res)
        oauth_user = OAuthUser()
        oauth_user.metadata = res
        oauth_user.picture = datas['avatar_url']
        oauth_user.nickname = datas['name']
        oauth_user.openid = datas['id']
        oauth_user.oauth_app = OAuthApp.objects.get(code='github')
        oauth_user.access_token = self.access_token
        if self.refresh_token:
            oauth_user.refresh_token = self.refresh_token
        if datas.get('email', False):
            oauth_user.email = datas['email']
        return oauth_user


class GoogleOAuthManager(ProxyManagerMixin, BaseOAuthManager):
    """
    Google OAuth Manager
    """
    AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
    TOKEN_URL = 'https://oauth2.googleapis.com/token'
    AUTH_PROVIDER_X509_CERT_URL = 'https://www.googleapis.com/oauth2/v1/certs'
    API_URL = 'https://www.googleapis.com/oauth2/v3/userinfo'
    CODE = 'google'
    NAME = '谷歌'

    def __init__(self, access_token=None, openid=None, refresh_token=None):
        config = self.get_config()
        self.project_id = config.project_id if config else ''
        self.client_id = config.app_key if config else ''
        self.client_secret = config.app_secret if config else ''
        self.callback_url = config.callback_url if config else ''

        super().__init__(access_token, openid, refresh_token)

    def get_authorization_url(self, next_url='/'):
        params = {
            'client_id': self.client_id,
            'response_type': 'code',
            # scope: 获取用户基础信息及邮箱权限
            'scope': 'openid email profile',
            'redirect_uri': self.callback_url,
            # 'state': state,
            'access_type': 'offline',
            'include_granted_scopes': 'true',
            'prompt': 'consent'
        }
        url = self.AUTH_URL + "?" + parse.urlencode(params)
        return url

    def get_access_token_by_code(self, code):
        params = {
            'code': code,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.callback_url,
            'grant_type': 'authorization_code',
        }

        res = self.post_url(self.TOKEN_URL, params=params)

        obj = json.loads(res)

        if 'access_token' in obj:
            self.access_token = obj.get('access_token', None)
            self.openid = obj.get('id_token', None)
            self.refresh_token = obj.get('refresh_token', None)
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def refresh_access_token(self, refresh_token):
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }

        res = self.post_url(self.TOKEN_URL, params=params)

        obj = json.loads(res)

        if 'access_token' in obj:
            self.access_token = obj.get('access_token', None)
            return self.access_token
        else:
            raise OAuthAccessTokenException(res)

    def get_oauth_userinfo(self):
        headers = {
            'Authorization': 'Bearer {}'.format(self.access_token)
        }
        res = self.get_url(self.API_URL, headers=headers)

        try:
            oauth_user = self.clean_info_res_data(res)
            return oauth_user
        except Exception as e:
            logger.error(e)
            logger.error('google oauth error res: ' + res)
            return None

    def clean_info_res_data(self, res) -> OAuthUser:
        datas = json.loads(res)
        oauth_user = OAuthUser()
        oauth_user.metadata = res
        oauth_user.picture = datas['picture']
        oauth_user.nickname = datas['name']
        oauth_user.openid = datas['sub']
        oauth_user.access_token = self.access_token
        oauth_user.oauth_app = OAuthApp.objects.get(code='google')
        if self.refresh_token:
            oauth_user.refresh_token = self.refresh_token
        if datas.get('email', False):
            oauth_user.email = datas['email']
        return oauth_user
