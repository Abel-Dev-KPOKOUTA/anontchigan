import joblib
import numpy as np
import os
from django.conf import settings
from keras.models import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Dropout, BatchNormalization, Input
from keras.optimizers import Adam
from keras.regularizers import l2
from PIL import Image
import h5py

class CancerPredictor:
    """
    Classe pour gérer les modèles de prédiction du cancer du sein
    """
    _tabular_model = None
    _image_model = None
    IMG_SIZE = 128  # Taille des images pour le modèle CNN
    
    # Classes pour le modèle d'images (exactement comme dans le code original)
    IMAGE_CLASSES = ["Non Malignant (No Cancer)", "Malignant"]
    
    @classmethod
    def build_image_model(cls):
        """
        Construit l'architecture du modèle CNN
        IDENTIQUE au code original - SANS augmentation pour la prédiction
        """
        REG = l2(0.01)
        
        model = Sequential([
            Input(shape=(cls.IMG_SIZE, cls.IMG_SIZE, 3)),
            
            Conv2D(32, 3, activation='relu', kernel_regularizer=REG),
            BatchNormalization(),
            MaxPool2D(),
            Conv2D(64, 3, activation='relu', kernel_regularizer=REG),
            BatchNormalization(),
            MaxPool2D(),
            Conv2D(128, 3, activation='relu', kernel_regularizer=REG),
            BatchNormalization(),
            MaxPool2D(),
            
            Flatten(),
            Dropout(0.6),
            Dense(128, activation='relu', kernel_regularizer=REG),
            Dropout(0.6),
            Dense(1, activation='sigmoid')
        ])
        
        opt = Adam(learning_rate=5e-4)
        model.compile(optimizer=opt, loss='binary_crossentropy', metrics=['accuracy'])
        return model
    
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
    def load_image_model(cls):
        """
        Charge le modèle Keras pour images
        EXACTEMENT comme dans le code original avec h5py
        """
        if cls._image_model is None:
            model_path = os.path.join(settings.BASE_DIR, 'predictor', 'models', 'mon_modele_cancer.keras')
            try:
                print(f"📂 Chargement du modèle depuis: {model_path}")
                
                # Créer l'architecture
                cls._image_model = cls.build_image_model()
                
                # Charger les poids avec h5py (comme dans le code original)
                with h5py.File(model_path, "r") as f:
                    print("📂 Clés dans le fichier:", list(f.keys()))
                    
                    for layer in cls._image_model.layers:
                        if layer.name in f['model_weights']:
                            weights = [
                                f['model_weights'][layer.name][w][:] 
                                for w in f['model_weights'][layer.name].keys()
                            ]
                            layer.set_weights(weights)
                
                print("✅ Poids chargés avec succès!")
                
            except FileNotFoundError:
                print(f"❌ ERREUR: Modèle introuvable à {model_path}")
                raise
            except Exception as e:
                print(f"❌ ERREUR lors du chargement: {e}")
                import traceback
                traceback.print_exc()
                raise
        return cls._image_model
    
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
    def predict_image(cls, image_path_or_file):
        """
        Fait une prédiction à partir d'une image
        EXACTEMENT comme dans le code original
        
        Args:
            image_path_or_file: Chemin vers l'image ou objet fichier Django
        
        Returns:
            dict: Résultat de la prédiction
        """
        model = cls.load_image_model()
        
        try:
            # Charger l'image (compatible avec Django UploadedFile et chemins)
            if hasattr(image_path_or_file, 'read'):
                # C'est un fichier uploadé Django
                img = Image.open(image_path_or_file).convert("RGB")
            else:
                # C'est un chemin de fichier
                img = Image.open(image_path_or_file).convert("RGB")
            
            # Redimensionner (comme dans le code original)
            img = img.resize((cls.IMG_SIZE, cls.IMG_SIZE))
            
            # Convertir en array et normaliser (comme dans le code original)
            img_array = np.array(img) / 255.0
            img_array = np.expand_dims(img_array, axis=0)
            
            # Prédiction (comme dans le code original)
            proba = float(model.predict(img_array, verbose=0)[0][0])
            
            # Classification (comme dans le code original)
            predicted_class = cls.IMAGE_CLASSES[int(proba >= 0.5)]
            confidence = max(proba, 1 - proba) * 100
            
            # Déterminer le label en français
            is_malignant = proba >= 0.5
            label = "Malin" if is_malignant else "Bénin"
            
            # Probabilités
            prob_malin = proba
            prob_benin = 1 - proba
            
            # Logs (comme dans le code original)
            print(f"🔬 Probabilité maligne: {proba:.1%}")
            print(f"🔬 Probabilité benign: {(1-proba):.1%}")
            print(f"🎯 Classe prédite: {predicted_class}")
            print(f"💪 Confiance: {confidence:.1f}%")
            
            return {
                'label': label,
                'probability': proba,
                'prob_malin': prob_malin,
                'prob_benin': prob_benin,
                'predicted_class': predicted_class,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de l'image: {e}")
            import traceback
            traceback.print_exc()
            raise
    
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