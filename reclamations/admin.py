from django.contrib import admin
from .models import Reclamation
from django.utils.html import format_html
from django.utils import timezone
from transformers import pipeline
from .admin_views import statistiques_admin 
from django.urls import path, reverse

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
    list_filter = ('statut', 'type_reclamation')
    search_fields = ('description', 'user__username')

    def statistiques_link(self, obj):
        return format_html(
            '<a class="button" href="{}">Voir Statistiques</a>',
            reverse('statistiques_admin')
        )
    statistiques_link.short_description = 'Actions'
    
    

    def save_model(self, request, obj, form, change):
        if obj.statut == 'Traité':
            if obj.date_traitement is None:
                obj.date_traitement = timezone.now()
            if obj.description:
                obj.reponse_admin = generate_response(obj.description)
            else:
                obj.reponse_admin = "Aucune réponse générée, description vide."
        super().save_model(request, obj, form, change)


    # Ajoutez cette méthode pour les URL personnalisées
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistiques/', self.admin_site.admin_view(statistiques_admin), name='statistiques_admin'),
        ]
        return custom_urls + urls

admin.site.register(Reclamation, ReclamationAdmin)
