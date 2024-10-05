from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Accès à l'interface d'admin Django
    path('', include('user.urls')),  # URLs de l'application "user"
]
