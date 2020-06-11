from django.shortcuts import render,redirect
from django.urls import reverse
from django.views import View
from home.models import ArticleCategory, Article, Comment
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotFound
import logging
from django.core.paginator import Paginator, EmptyPage
# Create your views here.


class IndexView(View):
    def get(self, request):
        user = request.user
        types = ArticleCategory.objects.all()
        articles = Article.objects.all()
        type_id = request.GET.get('type_id', 1)
        type = ArticleCategory.objects.get(id=type_id)

        context = {
            'types': types,
            'type': type,
            'user': user,
            'articles': articles,
        }
        return render(request, 'index.html', context)


class WriteBlogView(View):

    def get(self, reuqests):
        user = reuqests.user
        categories = ArticleCategory.objects.all()
        types = ArticleCategory.objects.all()

        context = {
            'user': user,
            'categories': categories,
            'types': types,
        }
        return render(reuqests, 'write_blog.html', context)

    def post(self, request):
        user = request.user
        avatar = request.FILES.get('avatar')
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        tags = request.POST.get('tags')
        sumary = request.POST.get('sumary')
        content = request.POST.get('content')

        if not all([avatar, title, category_id, tags, sumary, content]):
            print(content)
            return HttpResponseBadRequest('参数不全')

        try:
            category = ArticleCategory.objects.get(id=category_id)
        except ArticleCategory.DoesNotExist:
            return HttpResponseBadRequest('没有此分类')

        try:
            Article.objects.create(author=user, avatar=avatar, category=category, tags=tags, sumary=sumary, content=content)
        except Exception as e:
            logger = logging.getLogger('django')
            logger.error(e)
            return HttpResponseBadRequest('重新发布')

        return redirect(reverse('home:index'))

class DetailView(View):

    def get(self,request):

        id = request.GET.get('id')
        # 2.根据文章id进行文章数据的查询
        try:
            article = Article.objects.get(id=id)
        except Article.DoesNotExist:
            return HttpResponseNotFound('没有此文章')
        else:
            #让浏览量+1
            article.total_views += 1
            article.save()

        # 3.查询分类数据
        categories = ArticleCategory.objects.all()

        hot_articles = Article.objects.order_by('-total_views')[:9]

        # 4.获取分页请求参数
        page_size = request.GET.get('page_size',10)
        page_num = request.GET.get('page_num',1)
        # 5.根据文章信息查询评论数据
        comments = Comment .objects.filter(article=article).order_by('-created')

        total_count = comments.count()
        # 6.创建分页器

        paginator=Paginator(comments , page_size)
        # 7.进行分页处理
        try:
            page_comments=paginator.page(page_num)
        except EmptyPage:
            return HttpResponseNotFound('empty page')
        #总页数
        total_page = paginator.num_pages

        context={
            'categories': categories,
            'category': article.category,
            'article': article,
            'hot_articles': hot_articles,
            'total_count': total_count,
            'comments': page_comments,
            'page_size': page_size,
            'total_page': total_page,
            'page_num': page_num,
        }
        return render(request, 'detail.html', context=context)

    def post(self,request):
        user=request.user
        # 2.判断用户是否登录
        if user and user.is_authenticated:

            id = request.POST.get('id')
            content=request.POST.get('content')
            try:
                article=Article.objects.get(id=id)
            except Article.DoesNotExist:
                return HttpResponseNotFound('没有此文章')

            Comment.objects.create(
                content=content,
                article=article,
                user=user
            )
            #     3.4修改文章的评论数量
            article.comments_count+=1
            article.save()

            #刷新当前页面（页面重定向）
            path=reverse('home:detail')+'?id={}'.format(article.id)
            return redirect(path)
        else:
            # 4.未登录用户则跳转到登录页面
            return redirect(reverse('user:login'))


