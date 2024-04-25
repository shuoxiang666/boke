from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['name', 'email', 'content']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入您的姓名'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入您的邮箱'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': '请输入您的留言'}),
        }
