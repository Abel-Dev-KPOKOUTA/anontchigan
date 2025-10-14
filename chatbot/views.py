from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
from .services.rag_service import rag_service

def chatbot_page(request):
    """Vue pour afficher la page du chatbot"""
    return render(request, 'chatbot/chatbot.html')

@csrf_exempt
def chatbot_ask(request):
    """API endpoint pour traiter les questions du chatbot"""
    if request.method == 'POST':
        try:
            # Récupérer la question
            data = json.loads(request.body)
            question = data.get('question', '').strip()
            
            if not question:
                return JsonResponse({
                    'error': 'Question requise'
                }, status=400)
            
            # Utiliser le service RAG
            answer, match_type, score = rag_service.find_best_match(question)
            
            if answer:
                return JsonResponse({
                    "answer": answer,
                    "source": match_type,
                    "score": score,
                    "timestamp": timezone.localtime(timezone.now()).strftime('%d/%m/%Y à %H:%M'),
                })
            else:
                # Réponse de repli
                fallback_answer = rag_service.generate_fallback_response(question)
                return JsonResponse({
                    "answer": fallback_answer,
                    "source": "fallback",
                    "score": score,
                    "timestamp": timezone.localtime(timezone.now()).strftime('%d/%m/%Y à %H:%M'),
                })
            
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Format JSON invalide'
            }, status=400)
        except Exception as e:
            print(f"Erreur chatbot: {e}")
            return JsonResponse({
                'error': 'Une erreur s\'est produite'
            }, status=500)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)