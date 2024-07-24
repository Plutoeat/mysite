from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from django.utils import timezone

from blog.models import Category, Article
from comments.models import Comment
from utils.comments_utils import send_comment_email


# Create your tests here.
class CommentTest(TestCase):
    """
    评论测试
    """
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        from blog.models import BlogSettings
        value = BlogSettings()
        value.comment_need_review = True
        value.save()

    def update_article_comment_status(self, article):
        comments = article.comment_set.all()
        for comment in comments:
            comment.is_enable = True
            comment.save()

    def test_validate_comment(self):
        user = get_user_model().objects.create_superuser(
            email="admin@admin.com",
            username="admin",
            password="123456"
        )
        self.client.login(username="admin", password="123456")

        category = Category()
        category.name = "category1"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        article = Article()
        article.title = "title"
        article.body = "body"
        article.author = user
        article.category = category
        article.type = "article"
        article.status = "publish"
        article.save()

        comment_url = reverse('comments:postcomment', kwargs={'article_id': article.id})
        response = self.client.post(comment_url, {'body': 'test comment 1'})

        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(pk=article.pk)
        self.assertEqual(len(article.comment_list()), 0)
        self.update_article_comment_status(article)
        self.assertEqual(len(article.comment_list()), 1)

        response = self.client.post(comment_url, {'body': 'test comment 2'})

        self.assertEqual(response.status_code, 302)

        article = Article.objects.get(pk=article.pk)
        self.update_article_comment_status(article)
        call_command("clear_cache")
        self.assertEqual(len(article.comment_list()), 2)
        parent_comment_id = article.comment_list()[0].id

        response = self.client.post(comment_url, {
            'body': '''
                # Title1

                ```python
                import os
                ```

                [url](https://www.google.com/)

                [ddd](https://www.baidu.com/)

             ''',
            'parent_comment_id': parent_comment_id
        })

        self.assertEqual(response.status_code, 302)
        self.update_article_comment_status(article)
        article = Article.objects.get(pk=article.pk)
        call_command("clear_cache")
        self.assertEqual(len(article.comment_list()), 3)
        comment = Comment.objects.get(id=parent_comment_id)
        self.assertIsNotNone(comment)

        send_comment_email(comment)
