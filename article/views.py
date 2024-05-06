import markdown
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from taggit.models import Tag
from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm, ColumnForm
from comment.models import Comment
from comment.forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.core.serializers import serialize


def article_list(request):
    # 从查询字符串中获取搜索关键词、排序方式、栏目和标签
    search = request.GET.get('search', '')
    order = request.GET.get('order', '')
    column = request.GET.get('column', '')
    tag = request.GET.get('tag', '')

    # 获取所有文章
    article_list = ArticlePost.objects.all()

    # 如果有搜索关键词，则根据关键词过滤文章
    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(main__icontains=search) |
            Q(body__icontains=search)
        )

    # 如果有栏目筛选条件，则根据栏目筛选文章
    if column.isdigit():
        article_list = article_list.filter(column=column)

    # 如果有标签筛选条件，则根据标签筛选文章
    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    # 根据排序方式排序文章列表
    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    elif order == 'likes':
        article_list = article_list.order_by('-likes')

    # 分页处理
    paginator = Paginator(article_list, 8)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    # 构建上下文数据
    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)


def article_detail(request, id):
    # 获取文章对象
    article = get_object_or_404(ArticlePost, id=id)

    # 增加文章浏览量
    article.total_views += 1
    article.save(update_fields=['total_views'])

    # 获取上一篇和下一篇文章
    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id').first()
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id').first()

    # Markdown 渲染
    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)

    # 获取文章评论
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()

    # 构建上下文数据
    context = {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'toc': md.toc,
        'pre_article': pre_article,
        'next_article': next_article,
    }

    return render(request, 'article/detail.html', context)


@login_required(login_url='/userprofile/login/')
def article_create(request):
    # 处理表单提交
    if request.method == "POST":
        article_post_form = ArticlePostForm(request.POST, request.FILES)
        if article_post_form.is_valid():
            new_article = article_post_form.save(commit=False)
            new_article.author = request.user
            if request.POST['column'] != 'none':
                new_article.column = ArticleColumn.objects.get(id=request.POST['column'])
            new_article.save()
            article_post_form.save_m2m()
            return redirect("article:article_list")
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        # 显示创建文章的表单页面
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    # 获取要删除的文章对象
    article = get_object_or_404(ArticlePost, id=id)

    # 检查用户权限
    if request.user == article.author:
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("抱歉，你无权删除这篇文章。")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    # 获取要编辑的文章对象
    article = get_object_or_404(ArticlePost, id=id)

    # 检查用户权限
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    if request.method == "POST":
        # 处理表单提交
        article_post_form = ArticlePostForm(request.POST, instance=article)
        if article_post_form.is_valid():
            # 获取标签字符串并更新文章标签
            tags_str = article_post_form.cleaned_data['tags']
            tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            tags_str = ','.join(tags_list)
            article.tags.set(tags_str)
            article = article_post_form.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        # 显示文章编辑页面
        article_post_form = ArticlePostForm(instance=article)
        columns = ArticleColumn.objects.all()
        tags = Tag.objects.all()

        context = {'article': article, 'article_post_form': article_post_form, 'columns': columns, 'tags': tags}
        return render(request, 'article/update.html', context)


@login_required(login_url='/userprofile/login/')
def article_list_example(request):
    # 获取所有文章
    articles = ArticlePost.objects.all()

    # 构建上下文数据
    context = {'articles': articles}

    return render(request, 'article/list.html', context)


@login_required(login_url='/userprofile/login/')
def create_column(request):
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('article:article_list')
    else:
        form = ColumnForm()
    return render(request, 'article/column.html', {'form': form})


def top_three_posts(request):
    # 获取浏览量前三的文章
    top_posts = ArticlePost.objects.order_by('-total_views')[:3]

    # 将文章数据序列化为 JSON 格式
    top_posts_json = serialize('json', top_posts, fields=('title', 'total_views'))

    # 构建上下文数据
    return render(request, 'other/timeline.html', {'top_posts_json': top_posts_json})
