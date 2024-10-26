from django.contrib import admin
from .models import Blog, Article, Comment

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'published_at')
    search_fields = ('title', 'description', 'sujet', 'type')
    list_filter = ('published_at',)
    ordering = ('-created_at',)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'blog', 'author', 'created_at', 'published_at')
    search_fields = ('title', 'content')
    list_filter = ('published_at', 'blog')
    ordering = ('-created_at',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'article', 'created_at')
    search_fields = ('content',)
    list_filter = ('article',)
    ordering = ('-created_at',)
