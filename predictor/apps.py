from django.apps import AppConfig


class PredictorConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'predictor'
    verbose_name = 'Prédiction IA'
    
    def ready(self):
        """
        Code exécuté au démarrage de l'application
        Charge les modèles ML en mémoire
        """
        try:
            from .ml_utils import CancerPredictor
            
            # Précharger le modèle tabulaire
            try:
                CancerPredictor.load_tabular_model()
                print("✓ Modèle tabulaire préchargé")
            except Exception as e:
                print(f"⚠ Modèle tabulaire non chargé: {e}")
            
            # Précharger le modèle d'images
            try:
                CancerPredictor.load_image_model()
                print("✓ Modèle d'images préchargé")
            except Exception as e:
                print(f"⚠ Modèle d'images non chargé: {e}")
                
            print("✓ Module de prédiction initialisé")
        except Exception as e:
            print(f"⚠ Impossible de charger les modèles au démarrage: {e}")
            print("Les modèles seront chargés à la première prédiction")