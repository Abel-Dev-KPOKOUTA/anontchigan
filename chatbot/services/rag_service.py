import json
import os
from difflib import SequenceMatcher
import random
from django.conf import settings

class RAGService:
    def __init__(self):
        self.questions_data = []
        self.load_data()
    
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            file_path = os.path.join(settings.BASE_DIR, 'chatbot/data/cancer_sein.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Préparer les données pour la recherche
            for item in data:
                self.questions_data.append({
                    'question_originale': item['question'],
                    'question_normalisee': item['question'].lower().strip(),
                    'answer': item['answer']
                })
            print(f"✅ {len(self.questions_data)} questions chargées dans RAG")
            
        except FileNotFoundError:
            print("❌ Fichier cancer_sein.json non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement RAG: {e}")
    
    def similarity_score(self, str1, str2):
        """Calcule la similarité entre deux chaînes"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def find_by_keywords(self, user_question_lower):
        """Recherche par mots-clés spécifiques"""
        keyword_patterns = {
            'identite': {
                'keywords': ['qui es tu', 'qui es-tu', 'qui estu', 'present toi', 'presente toi', 'qui est anontchigan'],
                'search_in_json': ["Qui es-tu ?", "Comment tu t'appelles ?"]
            },
            'nom_signification': {
                'keywords': ['signifie ton nom', 'veut dire ton nom', 'signification nom', 'nom veut dire', 'anontchigan veut dire', 'que signifie anontchigan'],
                'search_in_json': ["Que signifie ton nom ?", "Pourquoi t'appelles-tu ANONTCHIGAN ?"]
            },
            'createurs': {
                'keywords': ['qui t a cree', 'qui ta cree', 'qui t a créé', 'qui ta créé', 'developpe par', 'créé par'],
                'search_in_json': ["Qui t'a créé ?", "Par qui as-tu été développé ?"]
            },
            'club_ia': {
                'keywords': ['club ia', 'club d ia', 'club intelligence', 'ensgmm', 'club deia'],
                'search_in_json': ["C'est quoi le club d'IA de l'ENSGMM ?"]
            },
            'mission': {
                'keywords': ['mission', 'objectif', 'but', 'pourquoi existe', 'pourquoi cree'],
                'search_in_json': ["Quelle est ta mission ?", "Quel est ton objectif ?"]
            }
        }
        
        for category, info in keyword_patterns.items():
            for keyword in info['keywords']:
                if keyword in user_question_lower:
                    for q in info['search_in_json']:
                        for item in self.questions_data:
                            if item['question_originale'] == q:
                                return item, 0.95
        return None, 0
    
    def find_best_match(self, user_question, threshold=0.6):
        """Trouve la meilleure correspondance"""
        user_q_lower = user_question.lower().strip()
        
        # Vérifier les salutations d'abord
        salutations = ["bonjour", "salut", "coucou", "hello", "akwe", "kpankpan", "yo", "bonsoir", "bjr", "hi"]
        if any(salut == user_q_lower for salut in salutations):
            responses = [
                "😊 Je suis ANONTCHIGAN 💗, votre assistante pour la sensibilisation au cancer du sein au Bénin. Je suis là pour vous accompagner avec bienveillance. Comment puis-je vous aider aujourd'hui ?",
                "💗 Ravie de vous parler ! Je suis ANONTCHIGAN, dédiée à la sensibilisation sur le cancer du sein. Parlons de prévention et d'auto-examen !",
                "😊 ANONTCHIGAN à votre service ! Je suis ici pour échanger sur l'importance du dépistage précoce. Quelle est votre question ?"
            ]
            return random.choice(responses), "salutation", 1.0
        
        best_match = None
        best_score = 0
        
        # 1. Recherche exacte
        for item in self.questions_data:
            if user_q_lower == item['question_normalisee']:
                return item['answer'], "exact", 1.0
        
        # 2. Recherche par similarité
        for item in self.questions_data:
            score = self.similarity_score(user_q_lower, item['question_normalisee'])
            if score > best_score:
                best_score = score
                best_match = item
        
        # 3. Recherche par mots-clés
        keywords_match, keywords_score = self.find_by_keywords(user_q_lower)
        if keywords_match and keywords_score > best_score:
            best_match = keywords_match
            best_score = keywords_score
        
        if best_match and best_score >= threshold:
            match_type = "exact" if best_score >= 0.9 else "similar"
            return best_match['answer'], match_type, best_score
        
        return None, "no_match", best_score
    
    def generate_fallback_response(self, question):
        """Génère une réponse de repli intelligente"""
        question_lower = question.lower()
        
        if any(mot in question_lower for mot in ['symptome', 'signe', 'detecter', 'remarquer']):
            return "Les signes du cancer du sein peuvent inclure : une boule dans le sein, un changement de forme ou de taille, un écoulement du mamelon, une rétraction de la peau. L'auto-examen mensuel aide à détecter ces changements précocement. En cas de doute, consultez un médecin. 💗"
        
        elif any(mot in question_lower for mot in ['traitement', 'soigner', 'guerir', 'therapie']):
            return "Le traitement du cancer du sein dépend du stade et peut inclure la chirurgie, la chimiothérapie, la radiothérapie ou l'hormonothérapie. Au Bénin, des centres spécialisés offrent ces soins. Le dépistage précoce améliore considérablement les chances de guérison. 🏥"
        
        elif any(mot in question_lower for mot in ['prevention', 'eviter', 'proteger', 'risque']):
            return "Pour réduire les risques : pratiquez l'auto-examen mensuel, maintenez un poids santé, limitez l'alcool, allaitez si possible, et faites des mammographies régulières après 40 ans. La détection précoce sauve des vies ! 💪"
        
        else:
            return "Je n'ai pas trouvé d'information spécifique sur ce point dans ma base de données. Cependant, je vous encourage vivement à pratiquer l'auto-examen mensuel et à consulter un professionnel de santé pour toute question médicale. Votre santé est précieuse ! 💗"

# Instance globale du service
rag_service = RAGService()