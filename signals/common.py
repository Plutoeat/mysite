import _thread
import logging

from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal

from comments.models import Comment
from mysite import settings
from utils.comments_utils import send_comment_email
from utils.common import get_current_site, cache, expire_view_cache, delete_view_cache
from utils.spider_notify import SpiderNotify
from websys.models import EmailLog

logger = logging.getLogger(__name__)
send_email_signal = Signal(['subject', 'message', 'recipient_list'])


@receiver(send_email_signal)
def send_email_signal_handler(sender, **kwargs):
    """
    发送邮件，并记录
    :param sender: 信号发送者
    :param kwargs: 信号携带的其他信息
    """
    subject = kwargs['subject']
    message = kwargs['message']
    recipient_list = kwargs['recipient_list']

    msg = EmailMultiAlternatives(
        subject=subject,
        body=message,
        to=recipient_list,
        from_email=settings.DEFAULT_FROM_EMAIL
    )

    msg.content_subtype = "html"

    from websys.models import EmailLog
    log = EmailLog()
    log.subject = subject
    log.message = message
    log.recipients = ','.join(recipient_list)
    try:
        result = msg.send()
        log.send_result = result > 0
    except Exception as e:
        logger.error(f"失败邮箱号: {recipient_list}, {e}")
        log.send_result = False
    log.save()


@receiver(post_save)
def model_post_save_callback(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    post 信号处理
    :return:
    """
    clear_cache = False
    if isinstance(instance, EmailLog):
        return
    if 'get_full_url' in dir(instance):
        is_update_views = update_fields == {'views'}
        if not settings.TESTING and not is_update_views:
            try:
                notify_url = instance.get_full_url()
                SpiderNotify.baidu_notify([notify_url])
            except Exception as e:
                logger.error("notify spider", e)
        if not is_update_views:
            clear_cache = True
    if isinstance(instance, Comment):
        if instance.is_enable:
            path = instance.article.get_absolute_url()
            site = get_current_site().domain
            if site.find(':') > 0:
                site = site[0:site.find(':')]

            expire_view_cache(
                path,
                servername=site,
                port=80,
                key_prefix='blog_detail')
            if cache.get('seo_processor'):
                cache.delete('seo_processor')
            comment_cache_key = 'article_comments_{id}'.format(id=instance.article.id)
            cache.delete(comment_cache_key)

            delete_view_cache('article_comments', [str(instance.article.pk)])

            _thread.start_new_thread(send_comment_email, (instance,))

    if clear_cache:
        cache.clear()
