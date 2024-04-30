import markdown
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.views import View
from taggit.models import Tag

from .models import ArticlePost, ArticleColumn
from .forms import ArticlePostForm, ColumnForm
from comment.models import Comment
from comment.forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q


def article_list(request):
    search = request.GET.get('search', '')
    order = request.GET.get('order', '')
    column = request.GET.get('column', '')
    tag = request.GET.get('tag', '')

    article_list = ArticlePost.objects.all()

    if search:
        article_list = article_list.filter(
            Q(title__icontains=search) |
            Q(main__icontains=search) |
            Q(body__icontains=search)
        )

    if column.isdigit():
        article_list = article_list.filter(column=column)

    if tag and tag != 'None':
        article_list = article_list.filter(tags__name__in=[tag])

    if order == 'total_views':
        article_list = article_list.order_by('-total_views')
    elif order == 'likes':
        article_list = article_list.order_by('-likes')

    paginator = Paginator(article_list, 8)
    page = request.GET.get('page')
    articles = paginator.get_page(page)

    context = {
        'articles': articles,
        'order': order,
        'search': search,
        'column': column,
        'tag': tag,
    }

    return render(request, 'article/list.html', context)


def article_detail(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    article.total_views += 1
    article.save(update_fields=['total_views'])

    pre_article = ArticlePost.objects.filter(id__lt=article.id).order_by('-id').first()
    next_article = ArticlePost.objects.filter(id__gt=article.id).order_by('id').first()

    md = markdown.Markdown(
        extensions=[
            'markdown.extensions.extra',
            'markdown.extensions.codehilite',
            'markdown.extensions.toc',
        ]
    )
    article.body = md.convert(article.body)
    comments = Comment.objects.filter(article=id)
    comment_form = CommentForm()
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
        article_post_form = ArticlePostForm()
        columns = ArticleColumn.objects.all()
        context = {'article_post_form': article_post_form, 'columns': columns}
        return render(request, 'article/create.html', context)


@login_required(login_url='/userprofile/login/')
def article_delete(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    if request.user == article.author:
        article.delete()
        return redirect("article:article_list")
    else:
        return HttpResponse("抱歉，你无权删除这篇文章。")


@login_required(login_url='/userprofile/login/')
def article_update(request, id):
    article = get_object_or_404(ArticlePost, id=id)
    if request.user != article.author:
        return HttpResponse("抱歉，你无权修改这篇文章。")

    if request.method == "POST":
        article_post_form = ArticlePostForm(request.POST, instance=article)
        if article_post_form.is_valid():
            # 处理标签数据
            tags_str = article_post_form.cleaned_data['tags']
            tags_list = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
            tags_str = ','.join(tags_list)
            article.tags.set(tags_str)

            article = article_post_form.save()
            return redirect("article:article_detail", id=id)
        else:
            return HttpResponse("表单内容有误，请重新填写。")
    else:
        article_post_form = ArticlePostForm(instance=article)
        columns = ArticleColumn.objects.all()
        tags = Tag.objects.all()
        context = {'article': article, 'article_post_form': article_post_form, 'columns': columns, 'tags': tags}
        return render(request, 'article/update.html', context)


@login_required(login_url='/userprofile/login/')
class IncreaseLikesView(View):
    def post(self, request, *args, **kwargs):
        article = get_object_or_404(ArticlePost, id=kwargs.get('id'))
        article.likes += 1
        article.save()
        return HttpResponse('success')


@login_required(login_url='/userprofile/login/')
def article_list_example(request):
    articles = ArticlePost.objects.all()
    context = {'articles': articles}
    return render(request, 'article/list.html', context)


@login_required(login_url='/userprofile/login/')
def create_column(request):
    if request.method == 'POST':
        form = ColumnForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('article:article_list')  # 重定向到首页或其他页面
    else:
        form = ColumnForm()
    return render(request, 'article/column.html', {'form': form})
