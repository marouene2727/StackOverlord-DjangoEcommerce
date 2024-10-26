from django.db import models
from django.contrib.auth.models import User

class Reclamation(models.Model):
    TYPE_RECLAMATION_CHOICES = [
        ('Produit', 'Produit'),
        ('Service', 'Service'),
        ('Expérience utilisateur', 'Expérience utilisateur'),
        ('Autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('En attente', 'En attente'),
        ('En cours', 'En cours'),
        ('Traité', 'Traité'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type_reclamation = models.CharField(max_length=50, choices=TYPE_RECLAMATION_CHOICES)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='En attente')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)
    reponse_admin = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Réclamation de {self.user.username} - {self.type_reclamation}"

class ReclamationRapport(models.Model):
    date_creation = models.DateTimeField(auto_now_add=True)
    contenu = models.TextField()

    def __str__(self):
        return f"Rapport du {self.date_creation.strftime('%Y-%m-%d %H:%M:%S')}"