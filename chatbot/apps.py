from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self):
        """
        Cette méthode s'exécute UNE SEULE FOIS au démarrage de Django
        Parfait pour pré-charger les modèles lourds
        """
        # Éviter de charger pendant les migrations
        import sys
        if 'runserver' not in sys.argv and 'gunicorn' not in sys.argv[0]:
            return
        
        # Importer et initialiser les services
        from . import views
        
        print("🚀 Pré-chargement des modèles IA au démarrage...")
        views.initialize_services()
        print("✅ Modèles chargés ! Le chatbot sera instantané.")