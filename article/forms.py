from django import forms
from .models import ArticlePost, ArticleColumn
from .models import ArticleColumn


class ColumnForm(forms.ModelForm):
    class Meta:
        model = ArticleColumn
        fields = ['title']  # 在表单中显示的字段


class ArticlePostForm(forms.ModelForm):  # 编写文章
    class Meta:
        # 指明数据模型来源
        model = ArticlePost
        # 定义表单包含的字段
        fields = ('title', 'main', 'body', 'tags', 'avatar', 'belongs')


class ArticleColumnForm(forms.ModelForm):  # 编写栏目
    class Meta:
        # 指明数据模型来源
        model = ArticleColumn
        # 定义表单包含的字段
        fields = ('title',)
