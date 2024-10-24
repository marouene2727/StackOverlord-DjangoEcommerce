from django.urls import path
from . import views

urlpatterns = [
    path('soumettre/', views.soumettre_reclamation, name='soumettre_reclamation'),
    path('mes-reclamations/', views.liste_reclamations, name='liste_reclamations'),
]
