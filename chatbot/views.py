
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from bs4 import BeautifulSoup
import re
import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)

def chatbot_view(request):
    return render(request,'chatbot/chatbot.html')

@csrf_exempt
def chat_api(request):
    """API pour le chatbot qui appelle Streamlit et extrait le JSON"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode POST requise'}, status=405)
    
    try:
        # Récupérer les données
        data = json.loads(request.body)
        question = data.get('question', '').strip()
        user_id = data.get('user_id', 'anonymous')
        
        if not question:
            return JsonResponse({
                'status': 'error',
                'answer': 'Veuillez poser une question.',
                'method': 'error'
            })
        
        logger.info(f"📤 Question reçue: {question}")
        
        # Gestion des salutations simples
        salutations = ['bonjour', 'salut', 'hello', 'hi', 'bonsoir', 'coucou', 'cc']
        if question.lower().strip() in salutations:
            return JsonResponse({
                'status': 'success',
                'answer': '👋 Bonjour ! Je suis ANONTCHIGAN. Comment puis-je vous aider concernant le cancer du sein ?',
                'method': 'salutation'
            })
        
        # Construire l'URL Streamlit avec paramètres API
        streamlit_url = 'https://anontchigan-api.streamlit.app/'
        params = {
            'api': 'true',
            'question': question,
            'user_id': user_id
        }
        
        logger.info(f"🔗 Appel Streamlit: {streamlit_url}")
        
        # Faire la requête HTTP avec timeout généreux
        response = requests.get(
            streamlit_url,
            params=params,
            timeout=60,  # 60 secondes pour laisser le temps à Streamlit
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/json'
            }
        )
        
        if response.status_code != 200:
            raise Exception(f"Streamlit retourne le code {response.status_code}")
        
        logger.info(f"✅ Réponse Streamlit reçue ({len(response.text)} caractères)")
        
        # STRATÉGIE 1: Chercher le JSON directement dans le HTML
        # Streamlit utilise st.json() qui crée un élément <pre> avec le JSON
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Méthode 1: Chercher dans les balises <pre> (st.json génère ça)
        json_data = None
        pre_elements = soup.find_all('pre')
        
        for pre in pre_elements:
            text = pre.get_text().strip()
            try:
                # Essayer de parser comme JSON
                parsed = json.loads(text)
                if isinstance(parsed, dict) and 'answer' in parsed:
                    json_data = parsed
                    logger.info("✅ JSON trouvé dans <pre>")
                    break
            except json.JSONDecodeError:
                continue
        
        # Méthode 2: Chercher dans les balises <code>
        if not json_data:
            code_elements = soup.find_all('code')
            for code in code_elements:
                text = code.get_text().strip()
                try:
                    parsed = json.loads(text)
                    if isinstance(parsed, dict) and 'answer' in parsed:
                        json_data = parsed
                        logger.info("✅ JSON trouvé dans <code>")
                        break
                except json.JSONDecodeError:
                    continue
        
        # Méthode 3: Regex pour extraire n'importe quel JSON avec "answer"
        if not json_data:
            logger.warning("⚠️ JSON non trouvé dans <pre>/<code>, utilisation de regex...")
            # Chercher un pattern JSON avec "answer"
            json_pattern = r'\{[^{}]*"answer"\s*:\s*"[^"]*"[^{}]*\}'
            matches = re.findall(json_pattern, response.text)
            
            for match in matches:
                try:
                    parsed = json.loads(match)
                    if 'answer' in parsed:
                        json_data = parsed
                        logger.info("✅ JSON trouvé par regex")
                        break
                except json.JSONDecodeError:
                    continue
        
        # Méthode 4: Regex plus large (multi-lignes)
        if not json_data:
            # Pattern pour capturer des JSON multi-lignes
            json_pattern_multi = r'\{[^{}]*"success"\s*:\s*(?:true|false)[^{}]*"answer"\s*:\s*"[^"]*"[^{}]*\}'
            matches = re.findall(json_pattern_multi, response.text, re.DOTALL)
            
            for match in matches:
                try:
                    # Nettoyer les sauts de ligne et espaces
                    cleaned = re.sub(r'\s+', ' ', match)
                    parsed = json.loads(cleaned)
                    if 'answer' in parsed:
                        json_data = parsed
                        logger.info("✅ JSON trouvé par regex multi-lignes")
                        break
                except json.JSONDecodeError:
                    continue
        
        # Méthode 5: Chercher directement le texte JSON dans tout le HTML
        if not json_data:
            logger.warning("⚠️ Dernière tentative: extraction brutale du JSON...")
            # Trouver tout ce qui ressemble à un objet JSON
            all_text = response.text
            
            # Chercher tous les { } et essayer de les parser
            start_positions = [i for i, char in enumerate(all_text) if char == '{']
            
            for start in start_positions:
                for end in range(start + 50, min(start + 2000, len(all_text))):
                    if all_text[end] == '}':
                        try:
                            candidate = all_text[start:end+1]
                            parsed = json.loads(candidate)
                            if isinstance(parsed, dict) and 'answer' in parsed:
                                json_data = parsed
                                logger.info(f"✅ JSON trouvé par extraction brutale")
                                break
                        except:
                            continue
                if json_data:
                    break
        
        # Si on a trouvé le JSON
        if json_data:
            answer = json_data.get('answer', '')
            method = json_data.get('method', 'groq_generated')
            
            logger.info(f"✅ Réponse extraite: {answer[:100]}...")
            
            return JsonResponse({
                'status': 'success',
                'answer': answer,
                'method': method,
                'user_id': user_id
            })
        
        # Si aucune méthode n'a fonctionné
        logger.error("❌ Impossible d'extraire le JSON")
        
        # Debug: sauvegarder le HTML pour inspection
        try:
            with open('/tmp/streamlit_debug.html', 'w', encoding='utf-8') as f:
                f.write(response.text)
            logger.info("💾 HTML sauvegardé dans /tmp/streamlit_debug.html pour debug")
        except:
            pass
        
        # Chercher au moins du texte lisible comme fallback
        body = soup.find('body')
        if body:
            text = body.get_text()
            # Chercher les lignes avec du contenu
            lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 30]
            if lines:
                # Prendre la ligne la plus pertinente
                for line in lines:
                    if any(word in line.lower() for word in ['cancer', 'sein', 'prévention', 'symptôme']):
                        logger.info(f"⚠️ Fallback: texte extrait")
                        return JsonResponse({
                            'status': 'success',
                            'answer': line,
                            'method': 'text_fallback'
                        })
        
        return JsonResponse({
            'status': 'error',
            'answer': "Désolé, je n'ai pas pu récupérer la réponse. Veuillez réessayer dans quelques instants.",
            'method': 'error'
        })
    
    except requests.Timeout:
        logger.error("⏱️ Timeout Streamlit")
        return JsonResponse({
            'status': 'error',
            'answer': "Le serveur met trop de temps à répondre. Veuillez patienter et réessayer.",
            'method': 'error'
        })
    
    except requests.RequestException as e:
        logger.error(f"🌐 Erreur réseau: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'answer': "Impossible de contacter le serveur Streamlit. Vérifiez votre connexion.",
            'method': 'error'
        })
    
    except Exception as e:
        logger.error(f"❌ Erreur inattendue: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return JsonResponse({
            'status': 'error',
            'answer': f"Une erreur s'est produite: {str(e)}",
            'method': 'error'
        })


@csrf_exempt
def health_check(request):
    """Vérifier que l'API fonctionne"""
    return JsonResponse({
        'status': 'online',
        'service': 'ANONTCHIGAN Django Chatbot API',
        'streamlit_url': 'https://anontchigan-api.streamlit.app/',
        'endpoints': {
            'chat': '/chatbot/api/chat/',
            'health': '/chatbot/api/health/'
        }
    })