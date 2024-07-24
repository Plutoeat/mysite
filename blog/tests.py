from django.core import mail
from django.core.management import call_command
from django.core.paginator import Paginator
from django.test import TestCase, Client, RequestFactory
from django.utils import timezone

from utils.common import send_email
from .models import *
from .templatetags.blog_tags import load_pagination


# Create your tests here.


class EmailTest(TestCase):
    """
    邮箱测试
    """
    def test_send_email(self):
        # 触发邮件发送的代码
        send_email(
            subject="Test Subject",
            message='Test email body',
            recipient_list=['test@test.com', ]
        )

        # 检查邮件是否发送
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')

        # 检查邮件内容
        self.assertEqual(mail.outbox[0].body, 'Test email body')
        self.assertIn('test@test.com', mail.outbox[0].to)


class ArticleTest(TestCase):
    """
    文章测试 命令测试
    """
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()

    def test_validate_article(self):
        site = get_current_site().domain
        user = get_user_model().objects.get_or_create(
            email="admin@admin.com",
            username="admin"
        )[0]
        user.set_password("123456")
        user.is_staff = True
        user.is_superuser = True
        user.save()
        response = self.client.get(user.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        response = self.client.get("/admin/websys/emaillog/")
        response = self.client.get("/admin/admin/logentry/")

        e = ExtraSection()
        e.sequence = 1
        e.name = "Test Section"
        e.content = "Test Content"
        e.is_enable = True
        e.save()

        category = Category()
        category.name = "category"
        category.created_time = timezone.now()
        category.last_mod_time = timezone.now()
        category.save()

        tag = Tag()
        tag.name = "Test Tag"
        tag.save()

        article = Article()
        article.title = "Test Article"
        article.body = "Test Content"
        article.author = user
        article.category = category
        article.status = "publish"
        article.type = "article"

        article.save()
        self.assertEqual(0, article.tags.count())
        article.tags.add(tag)
        article.save()
        self.assertEqual(1, article.tags.count())

        for i in range(20):
            article = Article()
            article.title = "nicetitle" + str(i)
            article.body = "nicetitle" + str(i)
            article.author = user
            article.category = category
            article.type = 'article'
            article.status = 'publish'
            article.save()
            article.tags.add(tag)
            article.save()
        from backends.documents import ELASTICSEARCH_ENABLED
        if ELASTICSEARCH_ENABLED:
            call_command("build_index")
        response = self.client.get('/search/', {'q': 'nicetitle'})
        self.assertEqual(response.status_code, 200)

        response = self.client.get(article.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        from utils.spider_notify import SpiderNotify
        SpiderNotify.notify(article.get_absolute_url())
        response = self.client.get(tag.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/search/', {'q': 'django'})
        self.assertEqual(response.status_code, 200)
        s = article.tags.all()
        self.assertIsNotNone(s)

        self.client.login(username='admin', password='123456')

        response = self.client.get(reverse('blog:archive'))
        self.assertEqual(response.status_code, 200)

        p = Paginator(Article.objects.all(), 2)
        self.__check_pagination__(p, '', '')

        p = Paginator(Article.objects.filter(tags=tag), 2)
        self.__check_pagination__(p, '标签', tag.name)

        p = Paginator(
            Article.objects.filter(
                author__username='admin'), 2)
        self.__check_pagination__(p, '作者', 'admin')

        p = Paginator(Article.objects.filter(category=category), 2)
        self.__check_pagination__(p, '分类', category.name)

        from utils.spider_notify import SpiderNotify
        SpiderNotify.baidu_notify([article.get_full_url()])

        link = Links(
            sequence=1,
            name="test",
            link='https://wwww.baidu.com',
            email="admin@admin.com"
        )
        link.save()
        response = self.client.get('/links/')
        self.assertEqual(response.status_code, 200)

        apply_data = {
            'link': "https://www.google.com/",
            'name': "谷歌",
            "email": "admin@admin.com",
            'master': "admin",
            "show_type": "home",
            "sequence": 0
        }
        response = self.client.post(reverse("blog:apply_roll"), apply_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], "/links/?status=success")

        response = self.client.get('/feed/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/rss/')
        self.assertEqual(response.status_code, 200)

        # response = self.client.get('/sitemap.xml')
        # self.assertEqual(response.status_code, 200)

        self.client.get("/admin/blog/article/1/delete/")
        self.client.get('/admin/websys/emaillog/')
        self.client.get('/admin/admin/logentry/')
        self.client.get('/admin/admin/logentry/1/change/')

    def __check_pagination__(self, p, type, value):
        s = load_pagination(None, p.page(1), type, value)
        self.assertIsNotNone(s)
        response = self.client.get(s['previous_url'])
        self.assertEqual(response.status_code, 200)
        response = self.client.get(s['next_url'])
        self.assertEqual(response.status_code, 200)

        s = load_pagination(None, p.page(2), type, value)
        self.assertIsNotNone(s)
        response = self.client.get(s['previous_url'])
        self.assertEqual(response.status_code, 200)
        response = self.client.get(s['next_url'])
        self.assertEqual(response.status_code, 200)

    def test_error_page(self):
        rsp = self.client.get('/error/')
        self.assertEqual(rsp.status_code, 404)

    def test_commands(self):
        from backends.documents import ELASTICSEARCH_ENABLED
        if ELASTICSEARCH_ENABLED:
            call_command("build_index")
        call_command("ping_baidu", "all")
        call_command("create_test_data")
        call_command("clear_cache")
