#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/4/10 17:36
# @Author  : Joker
# @File    : blog_tags.py
# @Software: PyCharm
import logging

from django import template
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.template.defaultfilters import stringfilter
from django.urls import reverse
from django.utils.safestring import mark_safe

from blog.models import Article, Category, Tag, ExtraSection, Links, LinkShowType
from comments.models import Comment
from utils.common import cache, CommonMarkdown

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag
def query(qs, **kwargs):
    """
    过滤参数
    :param qs: 实例
    :param kwargs: 条件
    :return: 过滤后的实例
    """
    return qs.filter(**kwargs)


@register.simple_tag
def dateformat(data):
    """
    日期格式化
    :param data: 时间
    :return: 格式化后的日期
    """
    try:
        return data.strftime(settings.DATE_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.simple_tag
def datetimeformat(data):
    """
    时间格式化
    :param data: 时间
    :return: 格式化后的时间
    """
    try:
        return data.strftime(settings.DATE_TIME_FORMAT)
    except Exception as e:
        logger.error(e)
        return ""


@register.simple_tag
def get_markdown_toc(content):
    body, toc = CommonMarkdown.get_markdown_with_all(content)
    return mark_safe(toc)


@register.filter
@stringfilter
def custom_markdown(content):
    """
    返回安全的 markdown 内容
    :param content: 内容
    :return: 安全的 markdown 内容
    """
    return mark_safe(CommonMarkdown.get_markdown(content))


@register.filter
@stringfilter
def strip_str(value: str, args):
    """
    去除字符串首尾的指定字符
    :param value: 字符串
    :param args: 字符
    :return: 去除字符串首尾指定字符后的字符串
    """
    if args:
        return value.strip(args)
    else:
        return value.strip('')


@register.inclusion_tag('base/tags/breadcrumb.html')
def load_breadcrumb(breadcrumbs):
    """
    加载面包屑
    :param breadcrumbs: 面包屑
    :return: 面包屑字典
    """
    return {'breadcrumbs': breadcrumbs}


@register.inclusion_tag('base/tags/footer_links.html')
def load_footer_links(link_type):
    """
    加载网页页脚的友情链接
    :param link_type: 页面类型
    :return: 友情链接字典
    """
    value = cache.get('footer_links')
    if value:
        return {'footer_links': value}
    else:
        logger.info("Loading footer links")
        links = Links.objects.filter(is_enable=True).filter(Q(show_type=link_type) | Q(show_type=LinkShowType.ALL))
        cache.set('footer_links', links, 60 * 60 * 60 * 3)
        logger.info('set footer_links cache.key:{key}'.format(key='footer_links'))
        return {'footer_links': links}


@register.inclusion_tag('blog/tags/article_list.html')
def load_article_list(article_list):
    """
    加载文章列表
    :param article_list: 文章列表
    :return: 文章列表字典
    """
    return {'article_list': article_list}


@register.inclusion_tag('blog/tags/search_article_list.html')
def load_search_article_list(article_list):
    """
    加载搜索结果列表
    :param article_list: 搜索结果列表
    :return: 搜索结果列表字典
    """
    return {'article_list': article_list}


@register.inclusion_tag('blog/tags/recent_articles.html')
def load_recent_articles(article_list):
    """
    加载最近文章列表
    :param article_list: 最近文章列表
    :return: 最近文章列表字典
    """
    return {'article_list': article_list}


@register.inclusion_tag('blog/tags/hot_articles.html')
def load_hot_articles():
    """
    加载热门文章列表
    :return: 热门文章列表字典
    """
    value = cache.get('hot_articles')
    if value:
        return {'article_list': value}
    else:
        logger.info('load hot articles')
        from utils.common import get_blog_setting
        blog_setting = get_blog_setting()
        hot_articles = Article.objects.filter(status='publish').order_by('-views')[
                             :blog_setting.hot_article_count]
        cache.set("hot_articles", hot_articles, 60 * 60 * 60 * 3)
        logger.info('set hot_articles cache.key:{key}'.format(key="hot_articles"))
        return {'article_list': hot_articles}


@register.inclusion_tag('blog/tags/recent_comment_articles.html')
def load_recent_comment_articles():
    """
    加载最近评论文章列表
    :return: 最近评论文章列表字典
    """
    value = cache.get('recent_comment_articles')
    if value:
        return value
    else:
        logger.info('load recent_comment_articles')
        from utils.common import get_blog_setting
        blog_setting = get_blog_setting()
        comment_list = Comment.objects.filter(is_enable=True).order_by('-id')[:blog_setting.comment_article_count]
        value = {
            'recent_comments': comment_list,
            'open_site_comment': blog_setting.open_site_comment,
        }
        cache.set("recent_comment_articles", value, 60 * 60 * 3)
        logger.info('set recent_comment_articles cache.key:{key}'.format(key='recent_comment_articles'))
        return value


@register.inclusion_tag('blog/tags/extra_sections.html')
def load_extra_sections():
    """
    加载额外内容
    :return: 额外内容
    """
    value = cache.get('extra_sections')
    if value:
        return {'extra_sections': value}
    else:
        logger.info('load extra_sections')
        extra_sidebars = ExtraSection.objects.filter(is_enable=True).order_by('sequence')
        cache.set("extra_sections", extra_sidebars, 60 * 60 * 3)
        logger.info('set extra_sections cache.key:{key}'.format(key='extra_sections'))
        return {'extra_sections': extra_sidebars}


@register.filter
def section_color_class(value):
    """
    额外内容背景颜色 奇数-纯白 偶数-灰色
    :param value:
    :return:
    """
    if value % 2 == 0:
        return 'bg-neutral-100 dark:bg-neutral-900'
    else:
        return 'bg-white dark:bg-black'


@register.inclusion_tag('blog/tags/pagination.html')
def load_pagination(paginator, page_obj, page_type, tag_name):
    """
    加载分页内容
    :param paginator: 分页器
    :param page_obj: 分页对象
    :param page_type: 页面类型
    :param tag_name: 查询参数
    :return: 分页内容字典
    """
    previous_url = ''
    next_url = ''
    if page_type == '':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse('blog:page', kwargs={'page': next_number})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:page', kwargs={
                    'page': previous_number})
    elif page_type == '分类':
        category = get_object_or_404(Category, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': next_number,
                    'category_name': category.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:category_detail_page',
                kwargs={
                    'page': previous_number,
                    'category_name': category.slug})
    elif page_type == '作者':
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': next_number,
                    'author_name': tag_name})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:author_detail_page',
                kwargs={
                    'page': previous_number,
                    'author_name': tag_name})
    elif page_type == '标签':
        tag = get_object_or_404(Tag, name=tag_name)
        if page_obj.has_next():
            next_number = page_obj.next_page_number()
            next_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': next_number,
                    'tag_name': tag.slug})
        if page_obj.has_previous():
            previous_number = page_obj.previous_page_number()
            previous_url = reverse(
                'blog:tag_detail_page',
                kwargs={
                    'page': previous_number,
                    'tag_name': tag.slug})
    return {
        'previous_url': previous_url,
        'next_url': next_url,
        'page_obj': page_obj,
        'paginator': paginator
    }
