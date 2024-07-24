from django.contrib.auth import get_user_model
from django.db import models

from blog.models import Article


# Create your models here.
class Comment(models.Model):
    """
    评论模型
    """
    body = models.TextField('正文', max_length=300)
    created_time = models.DateTimeField('创建时间', auto_now_add=True)
    last_mod_time = models.DateTimeField('修改时间', auto_now=True)
    author = models.ForeignKey(
        get_user_model(),
        verbose_name='作者',
        on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        verbose_name='文章',
        on_delete=models.CASCADE)
    parent_comment = models.ForeignKey(
        'self',
        verbose_name="上级评论",
        blank=True,
        null=True,
        on_delete=models.CASCADE)
    is_enable = models.BooleanField(
        '是否显示', default=False, blank=False, null=False)

    class Meta:
        ordering = ['-id']
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        get_latest_by = 'id'

    def __str__(self):
        return self.body
