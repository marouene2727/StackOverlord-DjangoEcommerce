from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),  # Accès à l'interface d'admin Django
    path('', include('user.urls')),  # URLs de l'application "user"
     path('reclamations/', include('reclamations.urls')),

    path('products/', include('products.urls')),  # URLs de l'application "products"

    path('articles/', include('blogs.urls')),

]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
