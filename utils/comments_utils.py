#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2024/7/22 22:33
# @Author  : Joker
# @File    : comments_utils.py
# @Software: PyCharm
import logging

from utils.common import get_current_site, send_email

logger = logging.getLogger(__name__)


def send_comment_email(comment):
    """
    发送邮件通知用户
    :param comment:
    :return:
    """
    site = get_current_site().domain
    subject = '感谢您发表的评论'
    article_url = "https://{site}{path}".format(
        site=site, path=comment.article.get_absolute_url())
    html_content = """
                   <p>非常感谢您在本站发表评论</p>
                   您可以访问
                   <a href="%s" rel="bookmark">%s</a>
                   来查看您的评论，
                   再次感谢您！
                   <br />
                   如果上面链接无法打开，请将此链接复制至浏览器。
                   %s
                   """ % (article_url, comment.article.title, article_url)
    to_email = comment.author.email
    send_email(subject, html_content, [to_email])
    try:
        if comment.parent_comment:
            html_content = """
                    您在 <a href="%s" rel="bookmark">%s</a> 的评论 <br/> %s <br/> 收到回复啦.快去看看吧
                    <br/>
                    如果上面链接无法打开，请将此链接复制至浏览器。
                    %s
                    """ % (article_url, comment.article.title, comment.parent_comment.body, article_url)
            to_email = comment.parent_comment.author.email
            send_email(subject, html_content, [to_email])
    except Exception as e:
        logger.error(e)
