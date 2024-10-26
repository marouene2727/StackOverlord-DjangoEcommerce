from django import forms
from django.contrib.auth.models import User
from .models import Article, Comment

class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = ['blog', 'title', 'content', 'published_at','image']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
