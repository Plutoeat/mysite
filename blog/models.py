import logging
from abc import abstractmethod

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField
from uuslug import slugify

from utils.common import cache, get_current_site, cache_decorator

logger = logging.getLogger(__name__)


# Create your models here.
class LinkShowType(models.TextChoices):
    HOME = ('home', '首页')
    LIST = ('list', '列表页')
    PAGE = ('page', '文章页面')
    ALL = ('all', '全站')
    BLOG_ROLL = ('blog_roll', '友情链接页面')


class BaseModel(models.Model):
    id = models.AutoField(primary_key=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    def save(self, *args, **kwargs):
        is_update_views = isinstance(
            self,
            Article) and 'update_fields' in kwargs and kwargs['update_fields'] == ['views']
        if is_update_views:
            Article.objects.filter(pk=self.pk).update(views=self.views)
        else:
            if 'slug' in self.__dict__:
                slug = getattr(self, 'title') if 'title' in self.__dict__ else getattr(self, 'name')
                setattr(self, 'slug', slugify(slug))
            super().save(*args, **kwargs)

    def get_full_url(self):
        site = get_current_site().domain
        url = "https://{site}{path}".format(site=site, path=self.get_absolute_url())
        return url

    class Meta:
        abstract = True

    @abstractmethod
    def get_absolute_url(self):
        pass


def author_directory_path(instance, filename: str) -> str:
    """
    返回一个最终文件存储路径
    :param instance: 实例
    :param filename: 文件名
    :return: 最终文件储存路径
    """
    return 'uploads/' + str(instance.author.id) + f'/{filename}'


class Article(BaseModel):
    """文章"""
    STATUS_CHOICES = (
        ('draft', '草稿'),
        ('publish', '发表'),
    )
    COMMENT_STATUS = (
        ('open', '打开'),
        ('close', '关闭'),
    )
    TYPE = (
        ('article', '文章'),
        ('page', '页面'),
    )
    title = models.CharField('标题', max_length=200, unique=True)
    slug = models.SlugField('处理后的标题', unique=True, null=True, blank=True, max_length=200)
    icon = models.CharField('图标', null=True, blank=True, max_length=200)
    cover = models.ImageField('封面', upload_to=author_directory_path, null=True, blank=True)
    body = MDTextField('正文')
    show_toc = models.BooleanField("是否显示toc目录", blank=False, null=False, default=False)
    category = models.ForeignKey('Category', verbose_name='分类', on_delete=models.CASCADE, blank=False, null=False)
    tags = models.ManyToManyField('Tag', verbose_name='标签集合', blank=True)
    author = models.ForeignKey(get_user_model(), verbose_name='作者', blank=False, null=False, on_delete=models.CASCADE)
    views = models.PositiveIntegerField('浏览量', default=0)
    article_order = models.IntegerField('排序,数字越大越靠前', blank=False, null=False, default=0)
    status = models.CharField('文章状态', max_length=20, choices=STATUS_CHOICES, default='draft')
    comment_status = models.CharField('评论状态', max_length=20, choices=COMMENT_STATUS, default='open')
    type = models.CharField('类型', max_length=20, choices=TYPE, default='article')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-article_order', '-created_time']
        verbose_name = "文章"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def get_meta_data(self):
        return self._meta

    def get_absolute_url(self):
        return reverse('blog:detailBySlug', kwargs={
            'slug': self.slug
        })

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        tree = self.category.get_category_tree()
        names = list(map(lambda c: (c.name, c.get_absolute_url()), tree))

        return names

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def viewed(self):
        self.views += 1
        self.save(update_fields=['views'])

    def comment_list(self):
        cache_key = 'article_comments_{id}'.format(id=self.id)
        value = cache.get(cache_key)
        if value:
            logger.info('get article comments:{id}'.format(id=self.id))
            return value
        else:
            comments = self.comment_set.filter(is_enable=True).order_by('-id')
            cache.set(cache_key, comments, 60 * 100)
            logger.info('set article comments:{id}'.format(id=self.id))
            return comments

    def get_admin_url(self):
        info = (self._meta.app_label, self._meta.model_name)
        return reverse('admin:%s_%s_change' % info, args=(self.pk,))

    @cache_decorator(expiration=60 * 100)
    def next_article(self):
        # 下一篇
        return Article.objects.filter(id__gt=self.id, status='publish').order_by('id').first()

    @cache_decorator(expiration=60 * 100)
    def previous_article(self):
        # 前一篇
        return Article.objects.filter(id__lt=self.id, status='publish').first()


class Category(BaseModel):
    """文章分类"""
    icon = models.CharField('图标', max_length=100, blank=True, null=True)
    name = models.CharField('分类名', max_length=30, unique=True)
    parent_category = models.ForeignKey('self', verbose_name="父级分类", blank=True, null=True,
                                        on_delete=models.CASCADE)
    slug = models.SlugField('处理后的标题', default='no-slug', max_length=60, blank=True)
    index = models.IntegerField(default=0, verbose_name="权重排序-越大越靠前")

    class Meta:
        ordering = ['-index']
        verbose_name = "分类"
        verbose_name_plural = verbose_name

    def get_absolute_url(self):
        return reverse(
            'blog:category_detail', kwargs={
                'category_name': self.slug})

    def __str__(self):
        return self.name

    @cache_decorator(60 * 60 * 10)
    def get_category_tree(self):
        """
        递归获得分类目录的父级
        :return:
        """
        category_list = []

        def parse(category):
            category_list.append(category)
            if category.parent_category:
                parse(category.parent_category)

        parse(self)
        return category_list

    @cache_decorator(60 * 60 * 10)
    def get_sub_category(self):
        """
        获得当前分类目录所有子集
        :return:
        """
        category_list = []
        all_category_list = Category.objects.all()

        def parse(category):
            if category not in category_list:
                category_list.append(category)
            child_list = all_category_list.filter(parent_category=category)
            for child in child_list:
                if category not in category_list:
                    category_list.append(child)
                parse(child)

        parse(self)
        return category_list

    def get_meta_data(self):
        return self._meta


class Tag(BaseModel):
    """文章标签"""
    icon = models.CharField('图标', max_length=100, blank=True, null=True)
    name = models.CharField('标签名', max_length=30, unique=True)
    slug = models.SlugField('处理后的标题', default='no-slug', max_length=60, blank=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('blog:tag_detail', kwargs={'tag_name': self.slug})

    @cache_decorator(60 * 60 * 10)
    def get_article_count(self):
        return Article.objects.filter(tags__name=self.name).distinct().count()

    class Meta:
        ordering = ['name']
        verbose_name = "标签"
        verbose_name_plural = verbose_name


def default_icon_path() -> str:
    """
    返回一个最终文件存储路径
    :return: 默认icon储存路径
    """
    return 'https://' + get_current_site().domain + '/static/base/image/logo-img.png'


class Links(models.Model):
    """友情链接"""
    name = models.CharField('链接名称', max_length=30, unique=True)
    link = models.URLField('链接地址')
    master = models.CharField('站长', max_length=50)
    email = models.EmailField('站长邮箱')
    icon = models.URLField('图标', blank=True, null=True)
    desc = models.TextField('简介', blank=True, null=True)
    notice = models.CharField('提示', max_length=30, blank=True, null=True)
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField(
        '是否显示', default=False, blank=False, null=False)
    show_type = models.CharField(
        '显示类型',
        max_length=9,
        choices=LinkShowType.choices,
        default=LinkShowType.HOME)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name

    def get_meta_data(self):
        return self._meta


class ExtraSection(models.Model):
    """额外区域, 首页处了固定内容可添加额外内容"""
    name = models.CharField('标题', max_length=100)
    content = models.TextField("内容")
    sequence = models.IntegerField('排序', unique=True)
    is_enable = models.BooleanField('是否启用', default=True)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        ordering = ['sequence']
        verbose_name = '额外内容'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


class BlogSettings(models.Model):
    """blog的配置"""
    site_name = models.CharField(
        "网站名称",
        max_length=200,
        null=False,
        blank=False,
        default='')
    site_description = models.TextField(
        "网站描述",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    site_seo_description = models.TextField(
        "网站SEO描述", max_length=1000, null=False, blank=False, default='')
    site_keywords = models.TextField(
        "网站关键字",
        max_length=1000,
        null=False,
        blank=False,
        default='')
    article_sub_length = models.IntegerField("文章摘要长度", default=300)
    hot_article_count = models.IntegerField("首页热门文章数目", default=7)
    comment_article_count = models.IntegerField("首页评论文章数目", default=8)
    article_comment_count = models.IntegerField("文章页面默认显示评论数目", default=5)
    show_google_adsense = models.BooleanField('是否显示谷歌广告', default=False)
    google_adsense_codes = models.TextField(
        '广告内容', max_length=2000, null=True, blank=True, default='')
    open_site_comment = models.BooleanField('是否打开网站评论功能', default=True)
    global_header = models.TextField("公共头部", null=True, blank=True, default='')
    global_footer = models.TextField("公共尾部", null=True, blank=True, default='')
    record_code = models.CharField(
        '备案号',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    analytics_code = models.TextField(
        "网站统计代码",
        max_length=1000,
        null=True,
        blank=True,
        default='')
    show_police_code = models.BooleanField(
        '是否显示公安备案号', default=False, null=False)
    police_record_code = models.TextField(
        '公安备案号',
        max_length=2000,
        null=True,
        blank=True,
        default='')
    comment_need_review = models.BooleanField(
        '评论是否需要审核', default=False, null=False)

    class Meta:
        verbose_name = '网站配置'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site_name

    def clean(self):
        if BlogSettings.objects.exclude(id=self.id).count():
            raise ValidationError(_('只能有一个配置'))

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from utils.common import cache
        cache.clear()
