import logging

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, HttpResponseForbidden, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import FormView
from ipware import get_client_ip

from accounts.forms import RegisterForm, LoginForm, ForgetPasswordForm, ForgetPasswordCodeForm, RequireEmailForm, \
    UserProfileForm
from accounts.models import OAuthUser, Profile
from accounts.oauth_exception import OAuthAccessTokenException
from utils.accounts_utils import set_user_status, get_verify_url, send_verify_email, verify_token, generate_code, \
    send_reset_email, set_code, verify_oauth_app, get_oauth_redirect_url, send_oauth_verify_email, verify_oauth_token, \
    send_oauth_success_email

logger = logging.getLogger(__name__)


# Create your views here.


class RegisterView(FormView):
    """
    注册逻辑
    """
    # 注册表单类
    form_class = RegisterForm
    # get 获取页面模板
    template_name = 'accounts/auth.html'
    # 额外上下文 表单类型和表单名称
    extra_context = {
        'form_type': 'register',
        'form_title': '注册'
    }

    # csrf_protect 保护站点免受跨站伪造站点攻击
    # 调度器，通过请求头判断不同返回
    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        """
        给额外上下文添加动态路径
        :param request: 用户请求 HttpRequest
        :param args: 其他输入列表
        :param kwargs: 其他输入字典
        :return: HttpResponse
        """
        # form_url: 表单提交路径
        form_url = reverse('accounts:register')
        # redirect_url: 表单下添加其他链接, 如: 立即登录 - 帮助已有账户的用户直接登录
        redirect_url_1 = reverse('accounts:login')
        self.extra_context.update({'form_url': form_url, 'redirect_url': [{'url': redirect_url_1, 'name': '立即登录'}]})
        return super(RegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        表单校验通过后逻辑
        :param form: RegisterForm 注册表单
        :return: 注册成功重定向到指定地址
        """
        # 进入注册，未验证邮箱定义为非活跃用户，无法登录
        user = set_user_status(form)
        # 拼接用户验证链接
        url = get_verify_url(user)
        # 发送验证邮件
        send_verify_email(url, user)
        redirect_url = reverse('accounts:result') + '?type=register&id=' + str(user.id)
        return HttpResponseRedirect(redirect_url)


class SignInView(LoginView):
    """
    登录逻辑, settings.py 文件中配置 LOGIN_URL, LOGIN_REDIRECT_URL 即可
    """
    template_name = 'accounts/auth.html'
    # 登录校验表单
    authentication_form = LoginForm
    # 登录记住有效期 7 天
    login_expiry = 60 * 60 * 24 * 7
    extra_context = {
        'form_type': 'login',
        'form_title': '登录'
    }

    def dispatch(self, request, *args, **kwargs):
        form_url = reverse('accounts:login')
        redirect_url_1 = reverse('accounts:register')
        redirect_url_2 = reverse('accounts:forget_password')
        self.extra_context.update({'form_url': form_url, 'redirect_url': [{'url': redirect_url_1, 'name': '立即注册'},
                                                                          {'url': redirect_url_2,
                                                                           'name': '忘记密码'}]})
        return super(SignInView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """
        如用户选择记住密码，密码有效期 7 天, 记录用户登录 IP
        :param form: LoginForm
        :return: HttpResponse
        """
        user = form.get_user()
        if self.request.POST.get('remember-me'):
            self.request.session.set_expiry(self.login_expiry)
        ip, _ = get_client_ip(self.request)
        user.last_login_IP = ip
        user.save()
        return super().form_valid(form)


class SignOutView(LogoutView):
    """
    登出逻辑, settings.py 文件中配置 LOGOUT_URL, LOGOUT_REDIRECT_URL 即可
    """
    pass


def account_result(request):
    """
    告知用户注册结果且需要验证邮箱，及邮箱验证结果
    :param request: 用户请求 HttpRequest
    :return: HttpResponse
    """
    get_type = request.GET.get('type')
    get_id = request.GET.get('id')

    user = get_object_or_404(get_user_model(), id=get_id)
    logger.info(get_type)
    if user.is_active:
        return HttpResponseRedirect('/')
    if get_type and get_type in ['register', 'validation']:
        if get_type == 'register':
            content = '''
                恭喜您注册成功，一封验证邮件已经发送到您的邮箱，请验证您的邮箱后登录本站。如没查收到邮件，可能在您的垃圾箱，请注意查收
            '''
            title = '注册成功'
        else:
            token = request.GET.get('token')
            if not verify_token(token, user):
                return HttpResponseForbidden()
            user.is_active = True
            user.save()
            content = '''
                恭喜您已经成功的完成邮箱验证，您现在可以使用您的账号来登录本站。
            '''
            title = '验证成功'
        return render(request, 'accounts/result.html', {
            'title': title,
            'content': content
        })
    else:
        return HttpResponseRedirect('/')


class ForgetPasswordView(FormView):
    """
    重置密码逻辑
    """
    form_class = ForgetPasswordForm
    template_name = 'accounts/auth.html'
    extra_context = {
        'form_type': 'forget_password',
        'form_title': '忘记密码'
    }

    def dispatch(self, request, *args, **kwargs):
        form_url = reverse('accounts:forget_password')
        redirect_url_1 = reverse('accounts:login')
        self.extra_context.update(
            {'form_url': form_url, 'redirect_url': [{'url': redirect_url_1, 'name': '立即登录'}]})
        return super(ForgetPasswordView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form: ForgetPasswordForm) -> HttpResponse:
        user = get_user_model().objects.filter(email=form.cleaned_data.get('email')).get()
        user.set_password(form.cleaned_data.get('new_password1'))
        user.save()
        return HttpResponseRedirect('/login/')


class ForgetPasswordEmailCode(View):
    """
    仅接受 post 请求, 根据获取的邮箱发送重置验证码
    """
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        form = ForgetPasswordCodeForm(request.POST)
        if not form.is_valid():
            return HttpResponse("error")
        to_email = form.cleaned_data.get('email')
        code = generate_code()
        send_reset_email(to_email, code)
        set_code(to_email, code)
        return HttpResponse("success")


def oauth_login(request):
    """
    跳转到第三方认证链接
    :param request: 用户请求 HttpRequest
    :return: HttpResponse
    """
    manager = verify_oauth_app(request)
    if not manager:
        return HttpResponseNotFound()
    next_url = get_oauth_redirect_url(request)
    authorize_url = manager.get_authorization_url(next_url)
    return HttpResponseRedirect(authorize_url)


def authorize(request):
    """
    授权用户登录
    :param request: 用户请求 HttpRequest
    :return: HttpResponse
    """
    manager = verify_oauth_app(request)
    if not manager:
        return HttpResponseNotFound()
    code = request.GET.get('code', None)
    next = request.GET.get('next', '/profile/')
    try:
        # 通过 code 获取 access_token 不必再去判断 是否返回 code
        manager.get_access_token_by_code(code)
    except OAuthAccessTokenException as e:
        logger.warning("OAuthAccessTokenException: " + str(e))
        return render(request, 'accounts/result.html', context={'title': '获取授权失败', 'content': '请尝试重新授权'})
    except Exception as e:
        logger.error(e)
        return render(request, 'accounts/result.html', context={'title': '获取授权失败', 'content': '请尝试重新授权'})
    oauth_user = manager.get_oauth_userinfo()
    # 存储 oauth 用户必要信息，需要重新授权
    if oauth_user:
        if not oauth_user.nickname or not oauth_user.nickname.strip():
            oauth_user.nickname = '用户_' + timezone.now().strftime('%y%m%d%I%M%S')
        try:
            temp = OAuthUser.objects.get(oauth_app=oauth_user.oauth_app, openid=oauth_user.openid)
            temp.picture = oauth_user.picture
            temp.metadata = oauth_user.metadata
            temp.nickname = oauth_user.nickname
            oauth_user = temp
        except ObjectDoesNotExist:
            pass
        # 判断用户是否已存在
        if oauth_user.email:
            # 确保数据库事务的原子性, 数据一致性和完整性
            with transaction.atomic():
                # 存在更新信息， 不存在创建一个用户
                user = None
                try:
                    user = get_user_model().objects.get(id=oauth_user.user_id)
                except ObjectDoesNotExist:
                    pass
                if not user:
                    result = get_user_model().objects.get_or_create(email=oauth_user.email)
                    user = result[0]
                    if result[1]:
                        try:
                            get_user_model().objects.get(username=oauth_user.nickname)
                        except ObjectDoesNotExist:
                            user.username = oauth_user.nickname
                        else:
                            user.username = '用户_' + timezone.now().strftime('%y%m%d%I%M%S')
                        user.is_active = True
                        user.source = "Authorize {}".format(request.GET.get('oauth_app', 'unknown'))
                        user.save()
                oauth_user.user = user
                oauth_user.save()

                # 登录
                login(request, user)
                return HttpResponseRedirect(next)
        else:
            logger.info(oauth_user)
            oauth_user.save()
            url = reverse('accounts:require_email', kwargs={'oauth_id': oauth_user.id})
            return HttpResponseRedirect(url)
    else:
        return render(request, 'accounts/result.html',
                      context={'title': '缺少重要信息', 'content': '请授权网站获取您的邮箱，用户名，头像'})


class RequireEmailView(FormView):
    """
    Oauth 登录信息缺少邮箱，补全邮箱逻辑
    """
    form_class = RequireEmailForm
    template_name = 'accounts/auth.html'
    extra_context = {
        'form_type': 'require_email',
        'form_title': '补全邮箱'
    }

    @method_decorator(csrf_protect)
    def dispatch(self, request, *args, **kwargs):
        oauth_id = self.kwargs['oauth_id']
        form_url = reverse('accounts:require_email', kwargs={
            'oauth_id': oauth_id
        })
        self.extra_context.update({'form_url': form_url})
        return super(RequireEmailView, self).dispatch(request, *args, **kwargs)

    def get_initial(self):
        oauth_id = self.kwargs['oauth_id']
        return {
            'email': '',
            'oauth_id': oauth_id
        }

    def form_valid(self, form):
        email = form.cleaned_data['email']
        oauth_id = form.cleaned_data['oauth_id']
        oauth_user = get_object_or_404(OAuthUser, pk=oauth_id)
        oauth_user.email = email
        oauth_user.save()
        send_oauth_verify_email(oauth_user)
        url = reverse('accounts:bind_success', kwargs={
            'oauth_id': oauth_id
        })
        url = url + '?required=email'
        return HttpResponseRedirect(url)


def bind_success(request, oauth_id):
    """
    绑定邮箱结果操作
    :param request: 用户请求 HttpRequest
    :param oauth_id: oauth 用户的 id
    :return: HttpResponse
    """
    required = request.GET.get('required', None)
    oauth_user = get_object_or_404(OAuthUser, pk=oauth_id)
    if required == 'email':
        title = '绑定成功'
        content = "恭喜您，还差一步就绑定成功了，请登录您的邮箱查看邮件完成绑定，谢谢。"
    else:
        title = '绑定成功'
        content = "恭喜您绑定成功，您以后可以使用{app_name}来直接免密码登录本站啦，感谢您对本站对关注。".format(
            app_name=oauth_user.oauth_app.app_name)
    return render(request, 'accounts/result.html', {
        'title': title,
        'content': content
    })


def email_verification(request, oauth_id, token):
    """
    验证邮箱, 成功绑定用户并登录
    :param request: 用户请求 HttpRequest
    :param oauth_id: oauth 用户 id
    :param token: 验证 16 进制令牌
    :return: HttpResponse
    """
    if not token:
        return HttpResponseForbidden()
    if not verify_oauth_token(token, oauth_id):
        return HttpResponseForbidden()
    oauth_user = get_object_or_404(OAuthUser, pk=oauth_id)
    with transaction.atomic():
        if oauth_user.user:
            user = get_user_model().objects.get(pk=oauth_user.user_id)
        else:
            result = get_user_model().objects.get_or_create(email=oauth_user.email)
            user = result[0]
            if result[1]:
                user.source = "Authorize {}".format(oauth_user.oauth_app.app_name)
                user.username = oauth_user.nickname.strip() if oauth_user.nickname.strip(
                ) else "用户_" + timezone.now().strftime('%y%m%d%I%M%S')
                user.save()
        oauth_user.user = user
        oauth_user.save()
    login(request, user)
    send_oauth_success_email(oauth_user)
    url = reverse('accounts:bind_success', kwargs={
        'oauth_id': oauth_id
    })
    url = url + '?required=success'
    return HttpResponseRedirect(url)


@login_required
def user_profile(request):
    """
    展示、修改用户的个人信息
    :param request: 用户请求
    :return: 用户个人信息
    """
    user = get_object_or_404(get_user_model(), pk=request.user.id)
    if request.method == "POST":
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()
            profile = request.user.profile_set
            for field in Profile._meta.fields:
                if field.name in ['avatar', 'gender', 'bio'] and form.cleaned_data[field.name] is not None:
                    setattr(profile, field.name, form.cleaned_data[field.name])
            profile.save()
            return HttpResponseRedirect("/profile/")
    else:
        form = UserProfileForm(instance=user)
    return render(request, 'accounts/profile.html', {'user': user, 'form': form})
