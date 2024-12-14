import logging

from django.core.paginator import Paginator
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView

from blog.forms import LinksForm
from blog.models import Article, LinkShowType, Category, Tag, Links
from comments.forms import CommentForm
from haystack.views import SearchView
from utils.common import cache, get_blog_setting

logger = logging.getLogger(__name__)


# Create your views here.


class ArticleListView(generic.ListView):
    """
    自定义列表视图
    """
    # template_name属性用于指定使用哪个模板进行渲染
    template_name = 'blog/article_index.html'

    # context_object_name属性用于给上下文变量取名（在模板中使用该名字）
    context_object_name = 'article_list'

    # 页面类型，分类目录或标签列表等
    page_type = ''
    paginate_by = 10
    page_kwarg = 'page'
    link_type = LinkShowType.LIST
    breadcrumbs = [
        ('首页', '/'),
    ]

    def get_view_cache_key(self):
        return self.request.GET['pages']

    @property
    def page_number(self):
        page_kwarg = self.page_kwarg
        page = self.kwargs.get(
            page_kwarg) or self.request.GET.get(page_kwarg) or 1
        return page

    def get_queryset_cache_key(self):
        """
        子类重写.获得queryset的缓存key
        """
        raise NotImplementedError()

    def get_queryset_data(self):
        """
        子类重写.获取queryset的数据
        """
        raise NotImplementedError()

    def get_queryset_from_cache(self, cache_key):
        """
        缓存页面数据
        :param cache_key: 缓存key
        :return:
        """
        value = cache.get(cache_key)
        if value:
            logger.info('get view cache.key:{key}'.format(key=cache_key))
            return value
        else:
            article_list = self.get_queryset_data()
            cache.set(cache_key, article_list)
            logger.info('set view cache.key:{key}'.format(key=cache_key))
            return article_list

    def get_queryset(self):
        """
        重写默认，从缓存获取数据
        :return:
        """
        key = self.get_queryset_cache_key()
        value = self.get_queryset_from_cache(key)
        return value

    def get_context_data(self, **kwargs):
        # 判断活跃界面
        if self.request.path == '/':
            kwargs['active_page'] = 'home'
            self.breadcrumbs = [
                ('首页', '/'),
            ]
        else:
            kwargs['active_page'] = self.request.path
        breadcrumbs = self.breadcrumbs
        if self.request.path != breadcrumbs[-1][1]:
            if len(breadcrumbs) <= 2:
                breadcrumbs.append(('第{}页'.format(self.page_number), self.request.path))
            else:
                breadcrumbs[-1] = ('第{}页'.format(self.page_number), self.request.path)
        kwargs['breadcrumbs'] = breadcrumbs
        kwargs['link_type'] = self.link_type
        return super(ArticleListView, self).get_context_data(**kwargs)


class HomeView(ArticleListView):
    """
    首页
    """
    paginate_by = 11
    link_type = LinkShowType.HOME

    def get_queryset_data(self):
        article_list = Article.objects.filter(status='publish')
        return article_list

    def get_queryset_cache_key(self):
        cache_key = 'blog_home'.format(page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        return super(HomeView, self).get_context_data(**kwargs)


class PageView(ArticleListView):
    """
    列表页
    """
    breadcrumbs = [
        ('首页', '/'),
        ('列表页', None),
    ]

    def get_queryset_data(self):
        article_list = Article.objects.filter(status='publish')
        return article_list

    def get_queryset_cache_key(self):
        cache_key = 'blog_page_{page}'.format(page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        return super(PageView, self).get_context_data(**kwargs)


class CategoryDetailView(ArticleListView):
    page_type = '分类'

    def get_queryset_data(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)

        category_name = category.name
        self.category_name = category_name
        category_names = list(map(lambda c: c.name, category.get_sub_category()))
        article_list = Article.objects.filter(category__name__in=category_names, status='publish')
        return article_list

    def get_queryset_cache_key(self):
        slug = self.kwargs['category_name']
        category = get_object_or_404(Category, slug=slug)

        category_name = category.name
        self.category_name = category_name
        cache_key = 'category_{category_name}_{page}'.format(category_name=category_name, page=self.page_number)
        return cache_key

    def get_context_data(self, **kwargs):
        category_name = self.category_name
        try:
            category_name = category_name.split('/')[-1]
        except AttributeError:
            pass
        if len(self.breadcrumbs) < 2:
            self.breadcrumbs.append((category_name, reverse('blog:category_detail',
                                                            kwargs={'category_name': self.kwargs['category_name']})))
        elif len(self.breadcrumbs) >= 2:
            if self.breadcrumbs[1][0] != category_name:
                self.breadcrumbs[1] = (category_name, reverse('blog:category_detail',kwargs={'category_name': self.kwargs['category_name']}))
        kwargs['page_type'] = CategoryDetailView.page_type
        kwargs['tag_name'] = category_name
        return super(CategoryDetailView, self).get_context_data(**kwargs)


class AuthorDetailView(ArticleListView):
    """
    作者文章页
    """
    page_type = '作者'

    def get_queryset_cache_key(self):
        from uuslug import slugify
        author_name = slugify(self.kwargs['author_name'])
        cache_key = 'author_{author_name}_{page}'.format(author_name=author_name, page=self.page_number)
        return cache_key

    def get_queryset_data(self):
        author_name = self.kwargs['author_name']
        article_list = Article.objects.filter(author__username=author_name, status='publish')
        return article_list

    def get_context_data(self, **kwargs):
        author_name = self.kwargs['author_name']
        if len(self.breadcrumbs) < 2:
            self.breadcrumbs.append((author_name, reverse('blog:author_detail', kwargs={'author_name': author_name})))
        elif len(self.breadcrumbs) >= 2:
            if self.breadcrumbs[1][0] != author_name:
                self.breadcrumbs[1] = (author_name, reverse('blog:author_detail', kwargs={'author_name': author_name}))
        kwargs['page_type'] = AuthorDetailView.page_type
        kwargs['tag_name'] = author_name
        return super(AuthorDetailView, self).get_context_data(**kwargs)


class TagDetailView(ArticleListView):
    """
    标签文章页
    """
    page_type = '标签'
    breadcrumbs = [
        ('首页', '/'),
    ]

    def get_queryset_cache_key(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        cache_key = 'tag_{tag_name}_{page}'.format(tag_name=tag_name, page=self.page_number)
        return cache_key

    def get_queryset_data(self):
        slug = self.kwargs['tag_name']
        tag = get_object_or_404(Tag, slug=slug)
        tag_name = tag.name
        self.name = tag_name
        article_list = Article.objects.filter(tags__name=tag_name, status='publish')
        return article_list

    def get_context_data(self, **kwargs):
        tag_name = self.name
        if len(self.breadcrumbs) < 2:
            self.breadcrumbs.append(
                (tag_name, reverse('blog:tag_detail', kwargs={'tag_name': self.kwargs['tag_name']})))
        elif len(self.breadcrumbs) >= 2:
            if self.breadcrumbs[1][0] != tag_name:
                self.breadcrumbs[1] = (tag_name, reverse('blog:tag_detail', kwargs={'tag_name': self.kwargs['tag_name']}))
        kwargs['page_type'] = TagDetailView.page_type
        kwargs['tag_name'] = tag_name
        return super(TagDetailView, self).get_context_data(**kwargs)


class ArticleDetailView(DetailView):
    """
    文章详情页
    """
    model = Article
    context_object_name = 'article'
    link_type = LinkShowType.PAGE

    def get_queryset(self):
        queryset = super(ArticleDetailView, self).get_queryset()
        return queryset.filter(status='publish')

    def get_object(self, queryset=None):
        obj = super(ArticleDetailView, self).get_object(queryset)
        obj.viewed()
        self.object = obj
        return obj

    def get_context_data(self, **kwargs):
        comment_form = CommentForm()

        article_comments = self.object.comment_list()
        parent_comments = article_comments.filter(parent_comment=None)
        blog_setting = get_blog_setting()
        paginator = Paginator(parent_comments, blog_setting.article_comment_count)
        breadcrumbs = self.object.get_category_tree()
        breadcrumbs.append(('首页', '/'))
        breadcrumbs = breadcrumbs[::-1]
        breadcrumbs.append((self.object.title, None))

        page = self.request.GET.get('comment_page', '1')
        if not page.isnumeric():
            page = 1
        else:
            page = int(page)
            if page < 1:
                page = 1
            if page > paginator.num_pages:
                page = paginator.num_pages

        p_comments = paginator.page(page)
        next_page = p_comments.next_page_number() if p_comments.has_next() else None
        previous_page = p_comments.previous_page_number() if p_comments.has_previous() else None

        if next_page:
            kwargs['comment_next_page_url'] = self.object.get_absolute_url() + f'?comment_page={next_page}#comments'
        if previous_page:
            kwargs[
                'comment_previous_page_url'] = self.object.get_absolute_url() + f'?comment_page={previous_page}#comments'

        # 获取文章后台地址
        info = (self.object._meta.app_label, self.object._meta.model_name)
        admin_link = reverse('admin:%s_%s_change' % info, args=(self.object.id,))

        kwargs['form'] = comment_form
        kwargs['article_comments'] = article_comments
        kwargs['p_comments'] = p_comments
        kwargs['comment_count'] = len(article_comments) if article_comments else 0
        kwargs['next_article'] = self.object.next_article
        kwargs['previous_article'] = self.object.previous_article
        kwargs['breadcrumbs'] = breadcrumbs
        kwargs['link_type'] = self.link_type
        kwargs['admin_link'] = admin_link
        return super(ArticleDetailView, self).get_context_data(**kwargs)

    def get_template_names(self):
        obj = self.get_object()
        if obj.type == 'page':
            template_name = 'blog/article_detail_page.html'
        else:
            template_name = 'blog/article_detail.html'
        return [template_name]


class ArchivesView(ArticleListView):
    """
    文章归档页面
    """
    page_type = '文章归档'
    paginate_by = None
    page_kwarg = None
    template_name = 'blog/article_archive.html'
    breadcrumbs = [
        ('首页', '/'),
        ('文章归档', '/archive/')
    ]

    def get_queryset_data(self):
        return Article.objects.filter(status='publish').all()

    def get_queryset_cache_key(self):
        cache_key = 'archive'
        return cache_key


class LinkListView(generic.ListView):
    """
    友情链接页
    """
    model = Links
    template_name = 'blog/links.html'
    extra_context = {
        'form': LinksForm,
        'breadcrumbs': [('首页', '/'), ('友情链接', None)]
    }

    def get_queryset(self):
        return Links.objects.filter(is_enable=True)

    def get_context_data(self, **kwargs):
        context = super(LinkListView, self).get_context_data(**kwargs)
        if self.request.GET.get('status') == 'success':
            context['success'] = '已成功申请友链，您的链接并不会立即出现在各个界面，需经过人工审核，结果会通过邮件及时告知'
        elif self.request.GET.get('status') == 'error':
            context['error_roll'] = '申请友链失败'
        return context


@csrf_protect
def apply_roll(request):
    """
    申请友情链接
    :param request: 用户请求
    :return: 重定向申请结果
    """
    if request.method == 'POST':
        form = LinksForm(request.POST)
        logger.info(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.sequence = Links.objects.count() + 1
            instance.save()
            return HttpResponseRedirect('/links/?status=success')
        for field, errors in form.errors.items():
            for error in errors:
                logger.error(f"Error in {field}: {error}")
        return HttpResponseRedirect('/links/?status=error')
    else:
        return HttpResponseForbidden()


class MySearchView(SearchView):
    """
    搜索视图
    """
    results_per_page = 10

    def get_context(self):
        paginator, page = self.build_page()
        context = {
            "query": self.query,
            "form": self.form,
            "page": page,
            "paginator": paginator,
            "suggestion": None,
            "breadcrumbs": [
                ('首页', '/'),
                ('搜素', None),
                (self.query, None)
            ]
        }
        if hasattr(self.results, "query") and self.results.query.backend.include_spelling:
            context["suggestion"] = self.results.query.get_spelling_suggestion()
        context.update(self.extra_context())
        return context


def permission_denied(request, exception, template_name='blog/error_page.html'):
    """
    权限不足视图
    :param request: 用户请求
    :param exception: 例外
    :param template_name: 模板名
    :return: 渲染页面
    """
    if exception:
        logger.error(exception)
    return render(request, template_name,
                  {'err_title': 'Oops', 'err_message': '您没有权限访问此页面。', 'status_code': '403'},
                  status=403)


def page_not_found(request, exception, template_name='blog/error_page.html'):
    """
    页面无法找到视图
    :param request: 用户请求
    :param exception: 例外
    :param template_name: 模板名
    :return: 渲染页面
    """
    if exception:
        logger.error(exception)
    return render(request, template_name,
                  {'err_title': '哎呀，出了一点问题', 'err_message': '对不起，我们找不到您的页面。', 'status_code': '404'},
                  status=404)


def server_error(request, template_name='blog/error_page.html'):
    """
    服务器意外视图
    :param request: 用户请求
    :param template_name: 模板名
    :return: 渲染页面
    """
    return render(request, template_name,
                  {'err_title': '哎呀，出错了', 'err_message': '我已收集错误信息，正在抓紧抢修中。', 'status_code': '500'},
                  status=500)
