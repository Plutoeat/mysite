#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/2/20 21:18
# @Author  : Joker
# @File    : urls.py
# @Software: PyCharm
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.decorators.cache import cache_page

from backends.elasticsearch_backend import ElasticSearchModelSearchForm
from blog import views
from blog.feeds import BlogFeed
from blog.sitemap import *

sitemaps = {
    'blog': ArticleSiteMap,
    'Category': CategorySiteMap,
    'Tag': TagSiteMap,
    'User': UserSiteMap,
    'static': StaticViewSitemap
}

app_name = 'blog'
urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('page/<int:page>/', views.PageView.as_view(), name='page'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='detailBySlug'),
    path('category/<slug:category_name>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('category/<slug:category_name>/<int:page>/', views.CategoryDetailView.as_view(), name='category_detail_page'),
    path('author/<str:author_name>/', views.AuthorDetailView.as_view(), name='author_detail'),
    path('author/<str:author_name>/<int:page>/', views.AuthorDetailView.as_view(), name='author_detail_page'),
    path('tag/<slug:tag_name>/', views.TagDetailView.as_view(), name='tag_detail'),
    path('tag/<slug:tag_name>/<int:page>/', views.TagDetailView.as_view(), name='tag_detail_page'),
    path('archive/', cache_page(60 * 60)(views.ArchivesView.as_view()), name='archive'),
    path('links/', views.LinkListView.as_view(), name='links'),
    path('links/apply/', views.apply_roll, name='apply_roll'),
    path('feed/', BlogFeed(), name='feed'),
    path('rss/', BlogFeed(), name='rss'),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="sitemaps",
    ),
    path('search/', views.MySearchView(form_class=ElasticSearchModelSearchForm), name='search'),
]
