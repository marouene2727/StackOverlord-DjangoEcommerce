from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Reclamation



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
    list_display = ('user', 'type_reclamation', 'statut', 'date_creation', 'date_traitement')
    list_filter = ('statut', 'type_reclamation')
    search_fields = ('description', 'user__username')

    def save_model(self, request, obj, form, change):
        if obj.statut == 'Traité' and obj.date_traitement is None:
            obj.date_traitement = timezone.now()
        super().save_model(request, obj, form, change)

admin.site.register(Reclamation, ReclamationAdmin)
