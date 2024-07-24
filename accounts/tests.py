import json
import logging
from unittest.mock import patch

from django.conf import settings
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse

from accounts.forms import ForgetPasswordForm
from accounts.models import User, OAuthConfig, OAuthApp, Profile
from accounts.oauth_manager import BaseOAuthManager
from utils.accounts_utils import get_verify_url, generate_code, set_code, send_reset_email, verify
from utils.common import get_sha256

logger = logging.getLogger(__name__)
# Create your tests here.


class AccountTest(TestCase):
    """
    Test case for Accounts model
    """
    def setUp(self):
        """
        Set up test
        """
        self.client = Client()
        self.factory = RequestFactory()
        self.test_user = User.objects.create_user(
            username="测试用户1",
            email="test@test1.com",
            password="12345678"
        )
        self.reset_password = '87654321Xx'

    def test_validate_register(self):
        """
        测试注册逻辑
        """
        # 1. 验证注册路由
        self.assertEquals(0, len(User.objects.filter(email='user123@user.com')))
        response = self.client.post(reverse('accounts:register'), {
            'username': 'user123',
            'email': 'user123@user.com',
            'password1': 'password123!q@wE#R$T',
            'password2': 'password123!q@wE#R$T',
        })
        self.assertEqual(1, len(User.objects.filter(email='user123@user.com')))
        # 2. 验证邮箱验证路由
        user = User.objects.filter(email='user123@user.com')[0]
        self.assertEqual(0, len(User.objects.filter(email='user123@user.com', is_active=True)))
        url = get_verify_url(user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(User.objects.filter(email='user123@user.com', is_active=True)))

    def test_validate_login(self):
        """
        测试登录逻辑
        """
        # 1. 验证登录功能
        response = self.client.get('/admin/')
        self.assertIn(response.status_code, [301, 302, 200])
        user = User.objects.create_superuser(
            email="admin@test.com",
            username="test-admin",
            password="123456"
        )
        login_result = self.client.login(
            username="test-admin",
            password="123456"
        )
        self.assertEqual(login_result, True)
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
        # 2. 验证登出功能
        response = self.client.post(reverse('accounts:logout'))
        self.assertIn(response.status_code, [301, 302, 200])
        # 3. 再次验证登录
        response = self.client.get('/admin/')
        self.assertIn(response.status_code, [301, 302, 200])
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test-admin',
            'password': '123456'
        })
        self.assertIn(response.status_code, [301, 302, 200])

    def test_verify_email_code(self):
        """
        测试发送、验证验证码逻辑
        """
        to_email = "admin@admin.com"
        code = generate_code()
        set_code(to_email, code)
        send_reset_email(to_email, code)

        err = verify("admin@admin.com", code)
        self.assertEqual(err, None)

        with self.assertRaises(ValidationError):
            verify("admin@123.com", code)

    def test_forget_password_email_code_success(self):
        """
        测试发送验证码逻辑成功
        """
        resp = self.client.post(
            path=reverse("accounts:forget_password_code"),
            data=dict(email="admin@admin.com")
        )

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode("utf-8"), "success")

    def test_forget_password_email_code_fail(self):
        """
        测试发送验证码逻辑失败
        """
        resp = self.client.post(
            path=reverse("accounts:forget_password_code"),
            data=dict()
        )
        self.assertEqual(resp.content.decode("utf-8"), "error")

        resp = self.client.post(
            path=reverse("accounts:forget_password_code"),
            data=dict(email="admin@com")
        )
        self.assertEqual(resp.content.decode("utf-8"), "error")

    def test_forget_password_email_success(self):
        """
        测试重置密码成功逻辑
        """
        code = generate_code()
        set_code(self.test_user.email, code)
        data = dict(
            new_password1=self.reset_password,
            new_password2=self.reset_password,
            email=self.test_user.email,
            code=code,
        )
        resp = self.client.post(
            path=reverse("accounts:forget_password"),
            data=data
        )
        self.assertEqual(resp.status_code, 302)

        # 验证用户密码是否修改成功
        test_user = User.objects.filter(
            email=self.test_user.email,
        ).first()
        self.assertNotEqual(test_user, None)
        self.assertEqual(test_user.check_password(data["new_password1"]), True)

    def test_forget_password_email_not_user(self):
        """
        测试重置密码, 找不到用户逻辑
        """
        code = generate_code()
        set_code(self.test_user.email, code)
        data = dict(
            new_password1=self.reset_password,
            new_password2=self.reset_password,
            email="123@123.com",
            code=code,
        )
        resp = self.client.post(
            path=reverse("accounts:forget_password"),
            data=data
        )

        self.assertEqual(resp.status_code, 200)
        self.assertFormError(
            form=ForgetPasswordForm(data=data),
            field="email",
            errors="未找到邮箱对应的用户"
        )

    def test_forget_password_email_code_error(self):
        """
        测试验证码错误逻辑
        """
        code = generate_code()
        set_code(self.test_user.email, code)
        data = dict(
            new_password1=self.reset_password,
            new_password2=self.reset_password,
            email=self.test_user.email,
            code="111111",
        )
        resp = self.client.post(
            path=reverse("accounts:forget_password"),
            data=data
        )

        self.assertEqual(resp.status_code, 200)
        self.assertFormError(
            form=ForgetPasswordForm(data=data),
            field="code",
            errors="验证码错误！"
        )

    def test_profile(self):
        """
        测试个人信息逻辑
        :return:
        """
        url = reverse("accounts:profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        login_url = reverse("accounts:login")
        self.assertTrue(login_url in response.url)

        user = User.objects.create_superuser(
            email="admin@test.com",
            username="test-admin",
            password="123456",
            nickname="test-admin"
        )

        profile = Profile.objects.create(
            user=user,
            avatar='avatar/1/1705243030048_mAZT7ZO.jpg',
            bio='12',
            gender='0',
        )

        login_result = self.client.login(
            username="test-admin",
            password="123456"
        )
        self.assertEqual(login_result, True)

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'test-admin')
        self.assertTemplateUsed(response, "accounts/profile.html")

        data = dict(
            nickname='test-change-admin',
            email='admin@test.com',
            phone_number="",
            avatar="avatar/1/1705243030048_mAZT7ZO.jpg",
            gender='0',
            bio="12"
        )
        response = self.client.post(url, data=data)
        print(response)
        self.assertEqual(response.status_code, 302)
        response = self.client.get(url)
        self.assertContains(response, "test-change-admin")


class OAuthConfigTest(TestCase):
    """
    测试 OAuthConfig 配置
    """
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_oauth_login(self):
        """
        测试 oauth 登录, 重定向到 app 获取 code
        """
        # 配置 OAuthConfig
        app = OAuthApp(
            code='gitee',
            app_name='码云'
        )
        app.save()
        config = OAuthConfig(
            oauth_app=app,
            project_id='123456',
            app_key='app_key',
            app_secret='app_secret',
            callback_url='callback_url',
            is_enable=True
        )
        config.save()

        url = reverse("accounts:oauth_login")
        response = self.client.get(url, data={'oauth_app': 'gitee'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue("gitee.com" in response.url)

        url = reverse("accounts:authorize")
        response = self.client.get(url, data={'oauth_app': 'gitee', 'code': 'code'})
        self.assertContains(response, '获取授权失败')


class OAuthLoginTest(TestCase):
    """
    oauth 登录逻辑测试
    """
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.apps = self.init_apps()

    def init_apps(self):
        applications = [p() for p in BaseOAuthManager.__subclasses__()]
        for application in applications:
            c = OAuthConfig()
            oauth_app = OAuthApp.objects.get_or_create(
                code=application.CODE,
                app_name=application.NAME,
            )
            c.oauth_app = oauth_app[0]
            c.app_key = 'app_key'
            c.app_secret = 'app_secret'
            c.is_enable = True
            c.save()
        return applications

    def get_app_by_oauth_app(self, oauth_app):
        for app in self.apps:
            if app.CODE.lower() == oauth_app:
                return app

    @patch("accounts.oauth_manager.GoogleOAuthManager.post_url")
    @patch("accounts.oauth_manager.GoogleOAuthManager.get_url")
    def test_google_login(self, mock_get_url, mock_post_url):
        """
        测试 Google oauth 登录
        :param mock_get_url: mock manager 的 get_url 方法
        :param mock_post_url: mock manager 的 post_url 方法
        :return:
        """
        google_app = self.get_app_by_oauth_app('google')
        assert google_app
        url = google_app.get_authorization_url()
        self.assertTrue("google.com" in url)
        self.assertTrue("client_id" in url)
        mock_post_url.return_value = json.dumps({
            "access_token": "access_token",
            "id_token": "id_token",
            "refresh_token": "refresh_token",
        })
        mock_get_url.return_value = json.dumps({
            "picture": "picture",
            "name": "name",
            "sub": "sub",
            "email": "email"
        })
        google_app.get_access_token_by_code('code')
        userinfo = google_app.get_oauth_userinfo()
        self.assertEqual(userinfo.access_token, 'access_token')
        self.assertEqual(userinfo.openid, 'sub')

    @patch("accounts.oauth_manager.GithubOAuthManager.post_url")
    @patch("accounts.oauth_manager.GithubOAuthManager.get_url")
    def test_github_login(self, mock_get_url, mock_post_url):
        """
        测试 GitHub oauth 登录
        :param mock_get_url: mock manager 的 get_url 方法
        :param mock_post_url: mock manager 的 post_url 方法
        :return:
        """
        github_app = self.get_app_by_oauth_app('github')
        assert github_app
        url = github_app.get_authorization_url()
        self.assertTrue("github.com" in url)
        self.assertTrue("client_id" in url)
        mock_post_url.return_value = "access_token=ghu_12345678&scope=repo,gist&token_type=bearer&refresh_token=ghu_12345678"
        mock_get_url.return_value = json.dumps({
            "avatar_url": "avatar_url",
            "name": "name",
            "id": "id",
            "email": "email"
        })
        github_app.get_access_token_by_code('code')
        userinfo = github_app.get_oauth_userinfo()
        self.assertEqual(userinfo.access_token, "ghu_12345678")
        self.assertEqual(userinfo.openid, 'id')

    @patch('accounts.oauth_manager.GiteeOAuthManager.post_url')
    @patch('accounts.oauth_manager.GiteeOAuthManager.get_url')
    def test_gitee_login_with_email(self, mock_get_url, mock_post_url):
        """
        测试 Gitee oauth 登录, 返回数据包含邮箱
        :param mock_get_url: mock manager 的 get_url 方法
        :param mock_post_url: mock manager 的 post_url 方法
        :return:
        """
        mock_post_url.return_value = json.dumps({
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        })

        mock_user_info = {
            "avatar_url": "avatar_url",
            "name": "name",
            "id": "id",
            "email": "email",
        }

        mock_get_url.return_value = json.dumps(mock_user_info)
        app = OAuthApp()
        app.code = 'gitee'
        app.app_name = '码云'
        app.save()
        response = self.client.get(reverse("accounts:oauth_login"), data={"oauth_app": "gitee"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue("gitee.com" in response.url)

        response = self.client.get(reverse("accounts:authorize"), data={
            "oauth_app": "gitee",
            "code": "code"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/')

        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['name'])
        self.assertEqual(user.email, mock_user_info['email'])
        self.client.logout()
        # 登出后再次登录 username 等信息不变
        response = self.client.get(reverse("accounts:authorize"), data={
            "oauth_app": "gitee",
            "code": "code"
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, '/profile/')

        user = auth.get_user(self.client)
        assert user.is_authenticated
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['name'])
        self.assertEqual(user.email, mock_user_info['email'])

    @patch('accounts.oauth_manager.GiteeOAuthManager.post_url')
    @patch('accounts.oauth_manager.GiteeOAuthManager.get_url')
    def test_gitee_login_without_email(self, mock_get_url, mock_post_url):
        """
        测试 Gitee oauth 登录, 返回数据不包含邮箱
        :param mock_get_url: mock manager 的 get_url 方法
        :param mock_post_url: mock manager 的 post_url 方法
        :return:
        """
        mock_post_url.return_value = json.dumps({
            "access_token": "access_token",
            "refresh_token": "refresh_token",
        })

        mock_user_info = {
            "avatar_url": "avatar_url",
            "name": "name",
            "id": "id",
        }

        mock_get_url.return_value = json.dumps(mock_user_info)
        app = OAuthApp()
        app.code = 'gitee'
        app.app_name = '码云'
        app.save()
        response = self.client.get(reverse("accounts:oauth_login"), data={"oauth_app": "gitee"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue("gitee.com" in response.url)

        # 没有邮箱, 跳转至补全邮箱页面
        response = self.client.get(reverse("accounts:authorize"), data={
            "oauth_app": "gitee",
            "code": "code"
        })
        self.assertEqual(response.status_code, 302)
        oauth_user_id = int(response.url.split('/')[-2])
        self.assertEqual(response.url, f'/oauth/require_email/{oauth_user_id}/')
        # 提交补全邮箱表单
        response = self.client.post(response.url, {'email': 'test@test.com', 'oauth_id': oauth_user_id})
        # 跳转至提示绑定页面
        self.assertEqual(response.status_code, 302)
        url = reverse("accounts:bind_success", kwargs={"oauth_id": oauth_user_id})
        self.assertEqual(response.url, f'{url}?required=email')
        # 邮箱确认
        token = get_sha256(get_sha256(settings.SECRET_KEY + str(oauth_user_id)))
        url = reverse("accounts:email_verification", kwargs={
            'oauth_id': oauth_user_id,
            'token': token,
        })
        response = self.client.get(url)
        # 跳转至绑定成功页面
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f'/oauth/bind_success/{oauth_user_id}/?required=success')

        user = auth.get_user(self.client)
        assert user.is_authenticated
        from accounts.models import OAuthUser
        oauth_user = OAuthUser.objects.get(user=user)
        self.assertTrue(user.is_authenticated)
        self.assertEqual(user.username, mock_user_info['name'])
        self.assertEqual(user.email, 'test@test.com')
        self.assertEqual(oauth_user.pk, oauth_user_id)
