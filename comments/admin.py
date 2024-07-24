import logging

from django.contrib import admin, messages
from django.urls import reverse
from django.utils.html import format_html
from django.utils.translation import ngettext

from comments.models import Comment

logger = logging.getLogger(__name__)


# Register your models here.
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    评论后台
    """
    list_per_page = 20
    list_display = (
        'id',
        'body',
        'link_to_userinfo',
        'link_to_article',
        'is_enable',
        'created_time'
    )
    list_display_links = ('id', 'body', 'is_enable')
    list_filter = ('is_enable', 'author', 'article',)
    exclude = ('created_time', 'last_mod_time')
    actions = ['disable_comments_status', 'enable_comments_status']

    @admin.display(description='用户')
    def link_to_userinfo(self, obj):
        info = (obj.author.get_meta_data().app_label, obj.author.get_meta_data().model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.author.id,))
        return format_html(
            u'<a href="%s">%s</a>' % (link, obj.author.nickname if obj.author.nickname else obj.author.email))

    @admin.display(description='文章')
    def link_to_article(self, obj):
        info = (obj.article.get_meta_data().app_label, obj.article.get_meta_data().model_name)
        link = reverse('admin:%s_%s_change' % info, args=(obj.article.id,))
        return format_html(
            u'<a href="%s">%s</a>' % (link, obj.article.title))

    @admin.action(description='禁用评论')
    def disable_comments_status(self, request, queryset):
        active = queryset.update(is_enable=False)
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章评论关闭",
                "成功将 %d 个文章评论关闭",
                active
            ) % active,
            messages.SUCCESS
        )

    @admin.action(description='启用评论')
    def enable_comments_status(self, request, queryset):
        active = queryset.update(is_enable=True)
        self.message_user(
            request,
            ngettext(
                "成功将 %d 个文章评论关闭",
                "成功将 %d 个文章评论关闭",
                active
            ) % active,
            messages.SUCCESS
        )
