from django.contrib import admin
from .models import ContactMessage, Newsletter

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les messages de contact
    """
    list_display = ('nom', 'email', 'sujet', 'date_envoi', 'traite')
    list_filter = ('sujet', 'traite', 'date_envoi')
    search_fields = ('nom', 'email', 'message')
    date_hierarchy = 'date_envoi'
    ordering = ('-date_envoi',)
    
    fieldsets = (
        ('Informations du contact', {
            'fields': ('nom', 'email', 'telephone')
        }),
        ('Message', {
            'fields': ('sujet', 'message')
        }),
        ('Gestion', {
            'fields': ('traite', 'date_envoi')
        }),
    )
    
    readonly_fields = ('date_envoi',)
    
    actions = ['marquer_comme_traite', 'marquer_comme_non_traite']
    
    def marquer_comme_traite(self, request, queryset):
        updated = queryset.update(traite=True)
        self.message_user(request, f"{updated} message(s) marqué(s) comme traité(s).")
    marquer_comme_traite.short_description = "Marquer comme traité"
    
    def marquer_comme_non_traite(self, request, queryset):
        updated = queryset.update(traite=False)
        self.message_user(request, f"{updated} message(s) marqué(s) comme non traité(s).")
    marquer_comme_non_traite.short_description = "Marquer comme non traité"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Interface d'administration pour les abonnés newsletter
    """
    list_display = ('email', 'nom', 'date_inscription', 'actif')
    list_filter = ('actif', 'date_inscription')
    search_fields = ('email', 'nom')
    date_hierarchy = 'date_inscription'
    ordering = ('-date_inscription',)
    
    actions = ['activer', 'desactiver']
    
    def activer(self, request, queryset):
        updated = queryset.update(actif=True)
        self.message_user(request, f"{updated} abonné(s) activé(s).")
    activer.short_description = "Activer"
    
    def desactiver(self, request, queryset):
        updated = queryset.update(actif=False)
        self.message_user(request, f"{updated} abonné(s) désactivé(s).")
    desactiver.short_description = "Désactiver"