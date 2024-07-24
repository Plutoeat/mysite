import logging

from django import forms
from django.contrib import admin, messages
from django.db import models
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ngettext
from mdeditor.widgets import MDEditorWidget

from blog.filter import ArticleListFilter
from blog.forms import ArticleForm
from blog.models import Article, Tag, Category, Links, ExtraSection, BlogSettings
from utils.common import send_email

logger = logging.getLogger(__file__)


# Register your models here.


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    文章后台
    """
    list_per_page = 20
    search_fields = ('body', 'title')
    form = ArticleForm
    list_display = (
        'id',
        'title',
        'author',
        'link_to_category',
        'created_time',
        'views',
        'status',
        'type',
        'article_order'
    )
    list_display_links = ('id', 'title')
    list_filter = (ArticleListFilter, 'status', 'type', 'category', 'tags')
    filter_horizontal = ('tags',)
    exclude = ('created_time', 'last_mod_time')
    view_on_site = True
    actions = [
        "make_article_publish",
        "draft_article",
        "close_article_comment_status",
        "open_article_comment_status"
    ]
    formfield_overrides = {
        models.TextField: {'widget': MDEditorWidget}
    }

    @admin.display(description="分类目录")
    def link_to_category(self, obj):
        info = (obj.category.get_meta_data().app_label, obj.category.get_meta_data().model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
        return format_html(u'<a href="%s">%s</a>' % (link, obj.category.name))

    @admin.action(description="发布选中文章")
    def make_article_publish(self, request, queryset):
        active = queryset.update(status='publish')
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章状态更改为发布",
                "成功将 %d 个文章状态更改为发布",
                active
            ) % active,
            messages.SUCCESS
        )

    @admin.action(description="选中文章设置为草稿")
    def draft_article(self, request, queryset):
        active = queryset.update(status='draft')
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章状态更改为草稿",
                "成功将 %d 个文章状态更改为发布",
                active
            ) % active,
            messages.SUCCESS
        )

    @admin.action(description="关闭文章评论")
    def close_article_comment_status(self, request, queryset):
        active = queryset.update(comment_status='close')
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章评论关闭",
                "成功将 %d 个文章评论关闭",
                active
            ) % active,
            messages.SUCCESS
        )

    @admin.action(description="打开文章评论")
    def open_article_comment_status(self, request, queryset):
        active = queryset.update(comment_status='open')
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章评论打开",
                "成功将 %d 个文章评论打开",
                active
            ) % active,
            messages.SUCCESS
        )

    def save_model(self, request, obj, form, change):
        super(ArticleAdmin, self).save_model(request, obj, form, change)

    def get_view_on_site_url(self, obj=None):
        if obj:
            url = obj.get_full_url()
            return url
        else:
            from utils.common import get_current_site
            site = get_current_site().domain
            return site


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    标签后台
    """
    exclude = ('slug', 'last_mod_time', 'created_time')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    分类后台
    """
    list_display = ('name', 'parent_category', 'index')
    exclude = ('slug', 'last_mod_time', 'created_time')


@admin.register(Links)
class LinksAdmin(admin.ModelAdmin):
    """
    友情链接后台
    """
    exclude = ('last_mod_time', 'created_time')
    list_display = ('name', 'is_enable', 'show_type', 'notice')
    actions = ["apply_roll"]

    class ConfirmActionForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        result = forms.ChoiceField(choices=[('True', '通过'), ('False', '拒绝')], label='结果')
        reason = forms.CharField(label='理由', max_length=255, required=False)

    @admin.action(description='审批友情链接申请')
    def apply_roll(self, request, queryset):
        form = None
        if 'cancel' in request.POST:
            self.message_user(request, u'已取消', messages.WARNING)
            return
        elif 'result' in request.POST:
            form = self.ConfirmActionForm(request.POST)
            if form.is_valid():
                result = form.cleaned_data['result'] == 'True'
                reason = form.cleaned_data['reason']
                active = queryset.update(is_enable=result)
                if result:
                    msg = '您的友链申请成功，请你确认您的链接已展示在网站，如有问题请及时联系'
                else:
                    msg = '您的友链申请未通过，未通过原因如下: ' + reason
                for item in queryset:
                    send_email(subject='友情链接申请结果', message=msg, recipient_list=[item.email])
                self.message_user(
                    request,
                    ngettext(
                        "已审批 %d 个友情链接申请",
                        "已审批 %d 个友情链接申请",
                        active
                    ) % active,
                    messages.SUCCESS
                )
                return HttpResponseRedirect(request.get_full_path())
            else:
                messages.warning(request, u'请选择结果')
                form = None

        if not form:
            selected_ids = request.POST.getlist('_selected_action')
            form = self.ConfirmActionForm(initial={'_selected_action': selected_ids})
        return render(request, 'blog/admin_apply_roll.html',
                      {'objs': queryset, 'form': form, 'path': request.get_full_path(), 'action': 'apply_roll',
                       'title': u'友情链接申请批量审核'})


@admin.register(ExtraSection)
class ExtraSectionAdmin(admin.ModelAdmin):
    """
    额外区域后台
    """
    list_display = ('name', 'content', 'is_enable', 'sequence')
    exclude = ('last_mod_time', 'created_time')


@admin.register(BlogSettings)
class BlogSettingsAdmin(admin.ModelAdmin):
    """
    博客网站设定后台
    """
    pass
