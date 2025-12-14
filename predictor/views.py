from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .ml_utils import CancerPredictor

# Page de prédiction
def prediction_page(request):
    """
    Vue pour afficher la page de prédiction
    """
    return render(request, 'predictor/prediction.html')


# API pour prédiction avec image (désactivée)
@require_http_methods(["POST"])
@csrf_exempt
def predict_image(request):
    """
    API endpoint pour analyser une image médicale
    DÉSACTIVÉ pour le déploiement (TensorFlow trop lourd)
    """
    return JsonResponse({
        'error': 'La prédiction par image n\'est pas disponible sur cette version déployée.',
        'message': 'Veuillez utiliser l\'analyse par données cliniques.',
        'feature_disabled': True
    }, status=503)


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
        print("📥 Données reçues:", data)

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

        print("🔍 Features préparées:", features)

        # Utiliser le modèle de prédiction
        try:
            result = CancerPredictor.predict(features)
            print("🎯 Résultat prédiction:", result)

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
        model_loaded = CancerPredictor._tabular_model is not None
        return JsonResponse({
            'model_loaded': model_loaded,
            'status': 'ready' if model_loaded else 'not_loaded',
            'image_model_available': False,
            'tabular_model_available': True
        })
    except Exception as e:
        return JsonResponse({
            'model_loaded': False,
            'status': 'error',
            'error': str(e)
        })