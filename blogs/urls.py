from django.urls import path
from django.conf import settings  # Ajoute cette ligne
from . import views
from django.conf.urls.static import static  # Ajoute cette ligne
from django.contrib.sitemaps.views import sitemap
from .sitemaps import ArticleSitemap
from .views import transcribe_audio
from .views import test_comment_analysis
from .views import sentiment_analysis_view

from .views import (
    article_list,
    article_detail,
    article_create,
    article_update,
    article_delete,
    comment_create,
    comment_update,
    comment_delete,
    transcribe_audio,  # Ajoutez cette ligne

)
sitemaps = {
    'articles': ArticleSitemap,
}
urlpatterns = [
    path('articles/', article_list, name='article_list'),
    path('articles/<int:pk>/', article_detail, name='article_detail'),  # Keep this line
    path('articles/create/', article_create, name='article_create'),
    path('articles/<int:pk>/update/', article_update, name='article_update'),
    path('articles/<int:pk>/delete/', article_delete, name='article_delete'),
    path('articles/<int:article_pk>/comments/create/', comment_create, name='comment_create'),
    path('articles/<int:article_pk>/comments/<int:comment_pk>/update/', comment_update, name='comment_update'),
    path('articles/<int:article_pk>/comments/<int:comment_pk>/delete/', comment_delete, name='comment_delete'),
    path('articles/transcribe/', transcribe_audio, name='transcribe_audio'),
    path('test-comment/', test_comment_analysis, name='test_comment_analysis'),
    path('article/<int:article_pk>/sentiment_analysis/', sentiment_analysis_view, name='sentiment_analysis'),

]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
