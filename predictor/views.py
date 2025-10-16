from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import numpy as np
from .ml_utils import CancerPredictor  # Import du prédicteur

# Page de prédiction
def prediction_page(request):
    """
    Vue pour afficher la page de prédiction
    """
    return render(request, 'predictor/prediction.html')

# API pour prédiction d'image
@require_http_methods(["POST"])
@csrf_exempt
def predict_image(request):
    """
    API endpoint pour analyser une image médicale
    """
    try:
        # Vérifier si une image a été envoyée
        if 'image' not in request.FILES:
            return JsonResponse({
                'error': 'Aucune image fournie'
            }, status=400)
        
        image_file = request.FILES['image']
        
        # Vérifier la taille du fichier (max 10MB)
        if image_file.size > 10 * 1024 * 1024:
            return JsonResponse({
                'error': 'Fichier trop volumineux (max 10MB)'
            }, status=400)
        
        # Vérifier le type de fichier
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image_file.content_type not in allowed_types:
            return JsonResponse({
                'error': 'Format non supporté. Utilisez JPG ou PNG.'
            }, status=400)
        
        # Simulation de prédiction (à remplacer par vrai modèle d'image)
        import random
        is_benign = random.choice([True, False])
        
        if is_benign:
            prob_malign = random.uniform(0.05, 0.35)
            label = "Bénigne"
        else:
            prob_malign = random.uniform(0.65, 0.95)
            label = "Maligne"
        
        return JsonResponse({
            'label': label,
            'prob_malign': prob_malign,
            'confidence': abs(prob_malign - 0.5) * 2,
            'message': 'Analyse complétée avec succès',
            'simulation': True
        })
        
    except Exception as e:
        print(f"Erreur lors de l'analyse d'image: {e}")
        return JsonResponse({
            'error': 'Une erreur s\'est produite lors de l\'analyse'
        }, status=500)

# API pour prédiction avec données tabulaires
@require_http_methods(["POST"])
@csrf_exempt
def predict_data(request):
    """
    API endpoint pour analyser des données cliniques
    """
    try:
        # Récupérer les données JSON
        data = json.loads(request.body)
        print("📥 Données reçues:", data)  # Debug
        
        # Valider les champs requis
        required_fields = [
            'age', 'radius', 'texture', 'perimeter', 'area', 
            'smoothness', 'compactness', 'concavity', 
            'concave_points', 'symmetry', 'fractal_dimension'
        ]
        
        for field in required_fields:
            if field not in data:
                return JsonResponse({
                    'error': f'Champ manquant: {field}'
                }, status=400)
        
        # Convertir les données
        try:
            age = float(data['age'])
            radius = float(data['radius'])
            texture = float(data['texture'])
            perimeter = float(data['perimeter'])
            area = float(data['area'])
            smoothness = float(data['smoothness'])
            compactness = float(data['compactness'])
            concavity = float(data['concavity'])
            concave_points = float(data['concave_points'])
            symmetry = float(data['symmetry'])
            fractal_dimension = float(data['fractal_dimension'])
        except ValueError as e:
            print(f"❌ Erreur conversion données: {e}")
            return JsonResponse({
                'error': 'Valeurs numériques invalides'
            }, status=400)
        
        # Validation des valeurs
        if not (18 <= age <= 120):
            return JsonResponse({'error': 'Âge invalide (18-120)'}, status=400)
        if radius < 0 or perimeter < 0 or area < 0:
            return JsonResponse({'error': 'Les dimensions doivent être positives'}, status=400)
        
        # Préparer les features pour le modèle
        features = {
            'radius': radius,
            'texture': texture,
            'perimeter': perimeter,
            'area': area,
            'smoothness': smoothness,
            'compactness': compactness,
            'concavity': concavity,
            'concave_points': concave_points,
            'symmetry': symmetry,
            'fractal_dimension': fractal_dimension
        }
        
        print("🔍 Features préparées:", features)  # Debug
        
        # Utiliser le modèle de prédiction
        try:
            result = CancerPredictor.predict(features)
            print("🎯 Résultat prédiction:", result)  # Debug
            
            if result:
                return JsonResponse({
                    'label': result['label'],
                    'prob_malign': result['prob_malin'],
                    'confidence': abs(result['prob_malin'] - 0.5) * 2,
                    'message': 'Calcul complété avec succès',
                    'model_used': True,
                    'factors': {
                        'age': age,
                        'radius': radius,
                        'texture': texture
                    }
                })
            else:
                raise Exception("La prédiction a retourné un résultat vide")
                
        except Exception as model_error:
            print(f"❌ Erreur modèle: {model_error}")
            # Fallback vers la simulation
            risk_score = 0
            if radius > 15: risk_score += 0.15
            if texture > 20: risk_score += 0.1
            if perimeter > 100: risk_score += 0.15
            if area > 700: risk_score += 0.15
            if smoothness > 0.1: risk_score += 0.1
            if compactness > 0.15: risk_score += 0.1
            if concavity > 0.1: risk_score += 0.1
            if concave_points > 0.05: risk_score += 0.1
            if symmetry > 0.2: risk_score += 0.05
            
            prob_malign = min(risk_score, 0.95)
            label = "Maligne" if prob_malign >= 0.5 else "Bénigne"
            
            return JsonResponse({
                'label': label,
                'prob_malign': prob_malign,
                'confidence': abs(prob_malign - 0.5) * 2,
                'message': 'Calcul complété avec succès (mode simulation)',
                'model_used': False,
                'factors': {
                    'age': age,
                    'radius': radius,
                    'texture': texture
                }
            })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Format JSON invalide'
        }, status=400)
    except Exception as e:
        print(f"❌ Erreur générale lors de l'analyse des données: {e}")
        return JsonResponse({
            'error': f'Une erreur s\'est produite lors du calcul: {str(e)}'
        }, status=500)

# Vue pour vérifier le statut du modèle
@csrf_exempt
def model_status(request):
    """
    Retourne le statut du modèle (pour debug)
    """
    try:
        from .ml_utils import CancerPredictor
        model_loaded = CancerPredictor._model is not None
        return JsonResponse({
            'model_loaded': model_loaded,
            'status': 'ready' if model_loaded else 'not_loaded'
        })
    except Exception as e:
        return JsonResponse({
            'model_loaded': False,
            'status': 'error',
            'error': str(e)
        })