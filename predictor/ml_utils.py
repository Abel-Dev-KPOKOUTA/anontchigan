import joblib
import numpy as np
import os
from django.conf import settings

class CancerPredictor:
    """
    Classe pour gérer le modèle de prédiction du cancer du sein
    """
    _model = None
    _model_loaded = False
    
    @classmethod
    def load_model(cls):
        """
        Charge le modèle joblib une seule fois (singleton pattern)
        """
        if cls._model is None:
            try:
                model_path = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'model_cancer_tabulaire.joblib')
                print(f"🔍 Recherche du modèle à: {model_path}")
                
                if not os.path.exists(model_path):
                    print(f"❌ Fichier modèle introuvable: {model_path}")
                    cls._model_loaded = False
                    return None
                
                cls._model = joblib.load(model_path)
                cls._model_loaded = True
                print("✅ Modèle de prédiction chargé avec succès")
                
                # Debug: informations sur le modèle
                if hasattr(cls._model, 'n_features_in_'):
                    print(f"📊 Modèle attend {cls._model.n_features_in_} features")
                
            except Exception as e:
                print(f"❌ ERREUR lors du chargement du modèle: {e}")
                cls._model_loaded = False
                cls._model = None
        
        return cls._model
    
    @classmethod
    def predict(cls, features):
        """
        Fait une prédiction à partir des caractéristiques
        """
        try:
            model = cls.load_model()
            if model is None:
                print("❌ Modèle non chargé")
                return None
            
            # Préparer les features dans le bon ordre
            feature_order = [
                'radius', 'texture', 'perimeter', 'area', 
                'smoothness', 'compactness', 'concavity', 
                'concave_points', 'symmetry', 'fractal_dimension'
            ]
            
            # Vérifier que toutes les features sont présentes
            for feature in feature_order:
                if feature not in features:
                    print(f"❌ Feature manquante: {feature}")
                    return None
            
            # Créer le tableau dans le bon ordre
            X = np.array([[features[f] for f in feature_order]])
            print(f"🔢 Features envoyées au modèle: {X}")
            
            # Prédiction
            prediction = model.predict(X)[0]
            print(f"🎯 Prédiction brute: {prediction}")
            
            # Probabilités
            try:
                probabilities = model.predict_proba(X)[0]
                prob_malin = float(probabilities[0])
                prob_benin = float(probabilities[1])
                print(f"📊 Probabilités: Malin={prob_malin:.3f}, Bénin={prob_benin:.3f}")
            except AttributeError:
                print("⚠ Le modèle ne supporte pas predict_proba")
                prob_malin = 1.0 if prediction == 0 else 0.0
                prob_benin = 1.0 - prob_malin
            
            # Déterminer le label (adaptez selon votre modèle)
            # Généralement: 0 = Malin, 1 = Bénin
            if prediction == 0:
                label = "Malin"
            else:
                label = "Bénin"
            
            print(f"🏷️ Label final: {label}")
            
            return {
                'label': label,
                'prediction': int(prediction),
                'prob_malin': prob_malin,
                'prob_benin': prob_benin,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Erreur lors de la prédiction: {e}")
            return None
    
    @classmethod
    def is_model_loaded(cls):
        """
        Vérifie si le modèle est chargé
        """
        return cls._model_loaded and cls._model is not None