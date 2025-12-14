import joblib
import numpy as np
import os
from django.conf import settings

class CancerPredictor:
    """
    Classe pour gérer le modèle de prédiction du cancer du sein (données tabulaires uniquement)
    """
    _tabular_model = None
    
    @classmethod
    def load_tabular_model(cls):
        """
        Charge le modèle joblib pour données tabulaires
        """
        if cls._tabular_model is None:
            model_path = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'model_cancer_tabulaire.joblib')
            try:
                cls._tabular_model = joblib.load(model_path)
                print("✅ Modèle tabulaire chargé avec succès")
            except FileNotFoundError:
                print(f"❌ ERREUR: Modèle tabulaire introuvable à {model_path}")
                raise
            except Exception as e:
                print(f"❌ ERREUR lors du chargement du modèle tabulaire: {e}")
                raise
        return cls._tabular_model
    
    @classmethod
    def predict(cls, features):
        """
        Fait une prédiction à partir des caractéristiques tabulaires
        """
        model = cls.load_tabular_model()
        
        # Préparer les features
        X = np.array([[
            features.get('radius', 0),
            features.get('texture', 0),
            features.get('perimeter', 0),
            features.get('area', 0),
            features.get('smoothness', 0),
            features.get('compactness', 0),
            features.get('concavity', 0),
            features.get('concave_points', 0),
            features.get('symmetry', 0),
            features.get('fractal_dimension', 0)
        ]])
        
        # Prédiction
        prediction = model.predict(X)[0]
        
        # Probabilités
        try:
            probabilities = model.predict_proba(X)[0]
            prob_malin = float(probabilities[0])
            prob_benin = float(probabilities[1])
        except AttributeError:
            prob_malin = 0.0 if prediction == 1 else 1.0
            prob_benin = 1.0 if prediction == 1 else 0.0
        
        # 0 = Malin, 1 = Bénin
        label = "Bénin" if prediction == 1 else "Malin"
        
        return {
            'label': label,
            'prediction': int(prediction),
            'prob_malin': prob_malin,
            'prob_benin': prob_benin,
            'probabilities': [prob_malin, prob_benin]
        }
    
    @classmethod
    def predict_simple(cls, X):
        """
        Version simplifiée
        """
        model = cls.load_tabular_model()
        if model.predict(X)[0] == 0:
            return "Malin"
        else:
            return "Bénin"