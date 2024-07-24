import logging
from django.contrib.auth.models import AbstractUser, Permission, GroupManager
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from django.utils.translation import gettext_lazy as _

from mysite import settings
from utils.common import get_current_site

logger = logging.getLogger(__name__)

# Create your models here.


class User(AbstractUser):
    """
    自定义认证 User, 在 settings.py 中配置 AUTH_USER_MODEL 生效
    """
    nickname = models.CharField('昵称', max_length=100, blank=True)
    phone_number = models.CharField(verbose_name="电话号码", max_length=11, null=True, blank=True, unique=True)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)
    groups = models.ManyToManyField(
        'XGroup',
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )
    last_login_IP = models.GenericIPAddressField(verbose_name="上次登录IP", null=True, blank=True)
    source = models.CharField(verbose_name="注册来源", max_length=100, blank=True)

    def get_absolute_url(self):
        return reverse('blog:author_detail', kwargs={'author_name': self.username})

    def __str__(self):
        return self.username

    def get_full_url(self):
        """
        获取 admin 在站点查看 url
        """
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    def get_meta_data(self):
        """
        获取 models 的 app_label 和 model_name, 返回 admin change_list 页面
        """
        return self._meta

    class Meta:
        ordering = ['-id']
        verbose_name = '用户'
        verbose_name_plural = verbose_name
        get_latest_by = 'id'


def user_directory_path(instance, filename: str) -> str:
    """
    返回一个最终文件存储路径
    :param instance: 实例
    :param filename: 文件名
    :return: 最终文件储存路径
    """
    return 'avatar/' + str(instance.user.id) + f'/{filename}'


class Profile(models.Model):
    """
    个人信息
    """
    GENDER = (
        (0, '男'),
        (1, '女'),
        (2, '外星人'),
    )
    avatar = models.ImageField(upload_to=user_directory_path, verbose_name="头像", name="avatar",
                               width_field="image_width",
                               height_field="image_height")
    gender = models.IntegerField(verbose_name="性别", choices=GENDER, null=True, blank=True)
    bio = models.CharField(verbose_name="简介", null=True, blank=True, max_length=25)
    date_of_birth = models.DateField(verbose_name="生日", null=True, blank=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='profile_set', on_delete=models.CASCADE)
    image_width = models.IntegerField(editable=False, null=True, blank=True)
    image_height = models.IntegerField(editable=False, null=True, blank=True)

    class Meta:
        ordering = ['-id']
        verbose_name = '档案'
        verbose_name_plural = verbose_name


class XGroup(models.Model):
    """
    重写一个 Group，自定已 AuthUser 后，旧 Group 不再可用
    """
    name = models.CharField(_("name"), max_length=150, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
    )

    objects = GroupManager()

    class Meta:
        verbose_name = _("group")
        verbose_name_plural = _("groups")

    def __str__(self):
        return self.name

    def natural_key(self):
        return (self.name,)


class OAuthApp(models.Model):
    """
    可用的第三方认证应用
    """
    code = models.CharField(verbose_name="代码", max_length=20, primary_key=True)
    app_name = models.CharField(verbose_name="app 名称", max_length=50)

    def __str__(self):
        return self.app_name

    class Meta:
        verbose_name = "oauth app"
        verbose_name_plural = verbose_name


class OAuthConfig(models.Model):
    """
    可用的第三方 app 的配置
    """
    oauth_app = models.OneToOneField(OAuthApp, on_delete=models.CASCADE)
    project_id = models.CharField(verbose_name="应用ID", max_length=300)
    app_key = models.CharField(verbose_name="AppKey", max_length=300)
    app_secret = models.CharField(verbose_name="AppSecret", max_length=300)
    callback_url = models.CharField(verbose_name="回调地址", blank=False, default='https://www.baidu.com',
                                    max_length=300)
    is_enable = models.BooleanField("是否使用", default=False, blank=False, null=False)
    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    updated_time = models.DateTimeField("更新时间", auto_now=True)

    def clean(self):
        if OAuthConfig.objects.filter(oauth_app=self.oauth_app).exclude(id=self.id).count():
            raise ValidationError(_(self.oauth_app.app_name + '已经存在'))

    def __str__(self):
        return self.oauth_app.app_name

    class Meta:
        verbose_name = "oauth 配置"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']


class OAuthUser(models.Model):
    """
    oauth 认证的用户
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="用户", blank=True, null=True,
                             on_delete=models.CASCADE)
    openid = models.CharField(max_length=50)
    nickname = models.CharField(verbose_name="昵称", max_length=50, null=True, blank=True)
    access_token = models.CharField(max_length=300, null=True, blank=True)
    refresh_token = models.CharField(max_length=300, null=True, blank=True)
    picture = models.CharField(max_length=350, blank=True, null=True)
    oauth_app = models.ForeignKey(OAuthApp, verbose_name="认证 app", on_delete=models.CASCADE)
    email = models.CharField(max_length=50, null=True, blank=True)
    metadata = models.TextField(null=True, blank=True)
    created_time = models.DateTimeField("创建时间", auto_now_add=True)
    updated_time = models.DateTimeField("更新时间", auto_now=True)

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = "oauth 用户"
        verbose_name_plural = verbose_name
        ordering = ['-created_time']
