from django.contrib import admin
from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    verbose_name = 'Prédiction IA'
    
    def ready(self):
        """
        Code exécuté au démarrage de l'application
        Peut être utilisé pour charger les modèles ML en mémoire
        """
        pass
        # TODO: Charger les modèles au démarrage
        # from .models import load_models
        # load_models()