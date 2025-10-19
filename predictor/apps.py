from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    verbose_name = 'Prédiction IA'
    
    def ready(self):
        """
        Code exécuté au démarrage de l'application
        Charge le modèle ML en mémoire
        """
        try:
            from .ml_utils import CancerPredictor
            # Précharger le modèle au démarrage
            CancerPredictor.load_model()
            print("✓ Module de prédiction initialisé")
        except Exception as e:
            print(f"⚠ Impossible de charger le modèle au démarrage: {e}")
            print("Le modèle sera chargé à la première prédiction")