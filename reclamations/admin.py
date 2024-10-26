from django.contrib import admin
from .models import Reclamation
from django.utils.html import format_html
from django.utils import timezone
from transformers import pipeline
from .admin_views import statistiques_admin 
from django.urls import path, reverse
from background_task import background

# Chargement du modèle de génération de texte
try:
    generator = pipeline('text-generation', model='gpt2')
except Exception as e:
    print(f"Erreur lors du chargement du modèle : {e}")
    generator = None

def generate_response(description):
    if generator:
        try:
            response = generator(f"Réponds à cette demande: {description}", max_length=50, num_return_sequences=1)
            return response[0]['generated_text']
        except Exception as e:
            print(f"Erreur lors de la génération de la réponse : {e}")
            return "Erreur de génération."
    return "Le générateur de texte n'est pas disponible."

@background(schedule=300)  # Exécute toutes les 10 minutes
def check_pending_reclamations():
    # Rechercher toutes les réclamations en attente
    pending_reclamations = Reclamation.objects.filter(statut='En attente')

    for reclamation in pending_reclamations:
        # Vérifier si 10 minutes se sont écoulées depuis la création de la réclamation
        if (timezone.now() - reclamation.date_creation).total_seconds() > 300:  # 600 secondes = 10 minutes
            if reclamation.statut == 'En attente':  # Vérifier si la réclamation est encore en attente
                # Générer une réponse pour chaque réclamation
                reclamation.reponse_admin = generate_response(reclamation.description)

                # Mettre à jour le statut et la date de traitement seulement après génération de la réponse
                reclamation.statut = 'Traité'  # Mettre à jour le statut
                reclamation.date_traitement = timezone.now()  # Mettre à jour la date de traitement
                reclamation.save()  # Enregistrer les modifications
                print(f"Réclamation traitée pour l'utilisateur: {reclamation.user.username}")
        else:
            print(f"La réclamation de l'utilisateur {reclamation.user.username} est toujours en attente.")
        print(f"La réclamation de l'utilisateur {reclamation.user.username} est toujours en attente.")

class StatutReclamationFilter(admin.SimpleListFilter):
    title = 'Statut de réclamation'
    parameter_name = 'statut_reclamation'

    def lookups(self, request, model_admin):
        return [
            ('En attente', 'En attente'),
            ('En cours', 'En cours'),
            ('Traité', 'Traité'),
        ]

    def queryset(self, request, queryset):
        if self.value() == 'En attente':
            return queryset.filter(statut='En attente')
        if self.value() == 'En cours':
            return queryset.filter(statut='En cours')
        if self.value() == 'Traité':
            return queryset.filter(statut='Traité')
        return queryset

class ReclamationAdmin(admin.ModelAdmin):
    list_display = ('user', 'type_reclamation', 'statut', 'date_creation', 'date_traitement', 'reponse_admin')
    list_filter = (StatutReclamationFilter,)  # Utiliser le filtre personnalisé
    search_fields = ('description', 'user__username')

    def statistiques_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Voir Statistiques</a>',
            reverse('statistiques_admin')
        )
    statistiques_link.short_description = 'Actions'
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)  # Enregistrer les modifications sans modifier le traitement automatique

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistiques/', self.admin_site.admin_view(statistiques_admin), name='statistiques_admin'),
        ]
        return custom_urls + urls

# Enregistrer le modèle dans l'admin
admin.site.register(Reclamation, ReclamationAdmin)

# Démarrer la tâche de vérification des réclamations en attente
check_pending_reclamations(repeat=300)  # Exécuter la tâche toutes les 10 minutes
