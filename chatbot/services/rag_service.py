import json
import os
import random
import numpy as np
from difflib import SequenceMatcher
from django.conf import settings

# Essayer d'importer les dépendances avancées
try:
    from sentence_transformers import SentenceTransformer
    import faiss
    HAS_ADVANCED_DEPS = True
except ImportError:
    HAS_ADVANCED_DEPS = False
    print("⚠️ Dépendances avancées non disponibles - Mode basique activé")

# Configuration Groq
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

class AdvancedRAGService:
    def __init__(self):
        self.questions_data = []
        self.embedding_model = None
        self.faiss_index = None
        self.groq_client = None
        self.use_groq = False
        
        self.load_data()
        self.initialize_advanced_features()
        self.initialize_groq()
    
    def load_data(self):
        """Charge les données depuis le fichier JSON"""
        try:
            file_path = os.path.join(settings.BASE_DIR, 'chatbot/data/cancer_sein.json')
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.questions_data = []
            self.all_texts = []
            
            for item in data:
                self.questions_data.append({
                    'question_originale': item['question'],
                    'question_normalisee': item['question'].lower().strip(),
                    'answer': item['answer']
                })
                self.all_texts.append(f"Question: {item['question']}\nRéponse: {item['answer']}")
            
            print(f"✅ {len(self.questions_data)} questions chargées")
            
        except FileNotFoundError:
            print("❌ Fichier cancer_sein.json non trouvé")
        except Exception as e:
            print(f"❌ Erreur chargement RAG: {e}")
    
    def initialize_advanced_features(self):
        """Initialise FAISS et les embeddings si disponibles"""
        if not HAS_ADVANCED_DEPS:
            print("⚠️ Mode basique - FAISS non disponible")
            return
        
        try:
            print("🔍 Initialisation des embeddings...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            print("📊 Création de l'index FAISS...")
            embeddings = self.embedding_model.encode(self.all_texts, show_progress_bar=False)
            embeddings = np.array(embeddings).astype('float32')
            
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings)
            
            print(f"✓ Index FAISS créé ({len(embeddings)} vecteurs, dim={dimension})")
            
        except Exception as e:
            print(f"❌ Erreur initialisation FAISS: {e}")
            self.embedding_model = None
            self.faiss_index = None
    
    def initialize_groq(self):
        """Initialise la connexion Groq"""
        if not GROQ_AVAILABLE:
            print("⚠️ Groq non disponible")
            return
        
        try:
            groq_api_key = getattr(settings, 'GROQ_API_KEY', None)
            if groq_api_key:
                self.groq_client = Groq(api_key=groq_api_key)
                self.use_groq = True
                print("✓ Groq configuré (Llama 3.1 8B Instant)")
            else:
                print("⚠️ Clé API Groq manquante dans les settings")
        except Exception as e:
            print(f"❌ Erreur configuration Groq: {e}")
    
    def similarity_score(self, str1, str2):
        """Calcule la similarité entre deux chaînes"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def search_faiss(self, query: str, k: int = 3):
        """Recherche dans FAISS"""
        if self.faiss_index is None or self.embedding_model is None:
            return []
        
        try:
            query_embedding = self.embedding_model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            distances, indices = self.faiss_index.search(query_embedding, k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx < len(self.questions_data):
                    similarity = 1 / (1 + distances[0][i])
                    results.append({
                        'question': self.questions_data[idx]['question_originale'],
                        'answer': self.questions_data[idx]['answer'],
                        'similarity': similarity,
                        'distance': distances[0][i]
                    })
            
            return results
        except Exception as e:
            print(f"❌ Erreur recherche FAISS: {e}")
            return []
    
    def find_by_keywords(self, user_question_lower):
        """Recherche par mots-clés spécifiques"""
        keyword_patterns = {
            'identite': {
                'keywords': ['qui es tu', 'qui es-tu', 'present toi', 'qui est anontchigan'],
                'search_in_json': ["Qui es-tu ?", "Comment tu t'appelles ?"]
            },
            'nom_signification': {
                'keywords': ['signifie ton nom', 'veut dire ton nom', 'signification nom'],
                'search_in_json': ["Que signifie ton nom ?", "Pourquoi t'appelles-tu ANONTCHIGAN ?"]
            },
            'createurs': {
                'keywords': ['qui t a cree', 'créé', 'developpe par', 'qui a fait', 'créateurs'],
                'search_in_json': ["Qui t'a créé ?", "Par qui as-tu été développé ?"]
            },
            'club_ia': {
                'keywords': ['club ia', 'club d ia', 'ensgmm'],
                'search_in_json': ["C'est quoi le club d'IA de l'ENSGMM ?"]
            }
        }
        
        for category, info in keyword_patterns.items():
            for keyword in info['keywords']:
                if keyword in user_question_lower:
                    for q in info['search_in_json']:
                        for item in self.questions_data:
                            if item['question_originale'] == q:
                                return item['answer'], 0.95
        return None, 0
    
    def generate_fallback_from_context(self, context: str) -> str:
        """Génère une réponse de secours basée sur le contexte"""
        try:
            lines = context.split('\n')
            answers = [line.strip() for line in lines if line.strip().startswith('R:')]
            
            if answers:
                first_answer = answers[0].replace('R:', '').strip()
                if len(first_answer) > 250:
                    first_answer = first_answer[:247] + "..."
                
                intro_phrases = [
                    "Écoute bien : ",
                    "Voilà ce que je peux te dire : ",
                    "Franchement : ",
                    "Je peux te dire que : ",
                    "D'après mes informations : "
                ]
                outro_phrases = [
                    " N'oublie pas de consulter un médecin !",
                    " Consulte un professionnel de santé.",
                    " Pense à voir un médecin pour plus de précisions.",
                    " La consultation médicale est importante."
                ]
                return f"{random.choice(intro_phrases)}{first_answer}{random.choice(outro_phrases)}"
            
            encouragement_phrases = [
                "C'est bien de te renseigner ! 💗 Pense à faire l'auto-examen chaque mois et consulte un médecin.",
                "Continue à t'informer ! 😊 Fais ton auto-examen régulièrement et consulte un professionnel.",
                "C'est important de s'informer ! 💗 Auto-examen + médecin = santé garantie !",
                "Tu fais bien de poser des questions 🔥 N'oublie pas : auto-examen tous les mois et check-up annuel."
            ]
            return random.choice(encouragement_phrases)
        except:
            return "Merci pour ta question ! 😊 Fais ton auto-examen régulièrement et consulte un médecin. 💗"
    
    def generate_with_groq(self, question: str, context: str) -> str:
        """Génère une réponse avec Groq"""
        if not self.use_groq or self.groq_client is None:
            return self.generate_fallback_from_context(context)
        
        try:
            # Optimiser le contexte
            context_lines = context.split('\n')[:8]
            context_short = '\n'.join(context_lines)
            
            if len(context_short) > 1000:
                context_short = context_short[:1000] + "..."
            
            messages = [
                {
                    "role": "system",
                    "content": """Tu es ANONTCHIGAN 💗, une assistante IA spécialisée dans la sensibilisation au cancer du sein.

Tu es bienveillante, professionnelle et concise. Utilise UNIQUEMENT les informations du contexte fourni.

RÈGLES:
- Sois directe et naturelle
- Utilise un langage clair et accessible
- Reste dans le domaine médical/santé
- Encourage la consultation médicale
- Sois concise (2-4 phrases maximum)"""
                },
                {
                    "role": "user",
                    "content": f"""CONTEXTE:
{context_short}

QUESTION: {question}

Réponds de manière directe et utile:"""
                }
            ]
            
            response = self.groq_client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Nettoyer la réponse
            unwanted_starts = ["bonjour", "salut", "hello", "coucou"]
            for phrase in unwanted_starts:
                if answer.lower().startswith(phrase):
                    answer = answer[len(phrase):].strip()
                    if answer and answer[0] in [',', '!', '.', ':']:
                        answer = answer[1:].strip()
                    if answer:
                        answer = answer[0].upper() + answer[1:]
            
            if not answer or len(answer) < 10:
                return self.generate_fallback_from_context(context)
            
            return answer
            
        except Exception as e:
            print(f"❌ Erreur Groq: {e}")
            return self.generate_fallback_from_context(context)
    
    def find_best_match_advanced(self, user_question):
        """Nouvelle méthode de recherche avancée"""
        user_q_lower = user_question.lower().strip()
        
        # 1. SALUTATIONS
        salutations = ["bonjour", "salut", "coucou", "hello", "akwe", "yo", "bonsoir", "hi"]
        if any(salut == user_q_lower for salut in salutations):
            responses = [
                "Bonjour ! 😊 Je suis ANONTCHIGAN, votre assistante pour la sensibilisation au cancer du sein. Comment puis-je vous aider ?",
                "Salut ! 👋 Ravie de vous parler. Vous avez une question sur le cancer du sein ?",
                "Hello ! 💗 ANONTCHIGAN à votre service. Quelle est votre question ?"
            ]
            return random.choice(responses), "salutation", 1.0
        
        # 2. RECHERCHE PAR MOTS-CLÉS
        keyword_answer, keyword_score = self.find_by_keywords(user_q_lower)
        if keyword_answer and keyword_score >= 0.9:
            return keyword_answer, "keyword_match", keyword_score
        
        # 3. RECHERCHE FAISS (si disponible)
        faiss_results = []
        if self.faiss_index:
            faiss_results = self.search_faiss(user_question, k=3)
        
        if not faiss_results:
            # Fallback vers la recherche par similarité basique
            return self.find_best_match_basic(user_question)
        
        best_result = faiss_results[0]
        similarity = best_result['similarity']
        
        # 4. DÉCISION : JSON vs GÉNÉRATION
        SIMILARITY_THRESHOLD = 0.65
        
        if similarity >= SIMILARITY_THRESHOLD:
            # HAUTE SIMILARITÉ → Réponse directe du JSON
            return best_result['answer'], "json_direct", similarity
        
        else:
            # FAIBLE SIMILARITÉ → Génération avec Groq ou fallback
            context_parts = []
            for i, result in enumerate(faiss_results[:3], 1):
                answer_truncated = result['answer']
                if len(answer_truncated) > 250:
                    answer_truncated = answer_truncated[:247] + "..."
                context_parts.append(f"{i}. Q: {result['question']}\n   R: {answer_truncated}")
            
            context = "\n\n".join(context_parts)
            generated_answer = self.generate_with_groq(user_question, context)
            
            return generated_answer, "groq_generated", similarity
    
    def find_best_match_basic(self, user_question):
        """Méthode de fallback basique (sans FAISS)"""
        user_q_lower = user_question.lower().strip()
        
        # Recherche exacte
        for item in self.questions_data:
            if user_q_lower == item['question_normalisee']:
                return item['answer'], "exact", 1.0
        
        # Recherche par similarité
        best_match = None
        best_score = 0
        
        for item in self.questions_data:
            score = self.similarity_score(user_q_lower, item['question_normalisee'])
            if score > best_score:
                best_score = score
                best_match = item
        
        if best_match and best_score >= 0.6:
            match_type = "exact" if best_score >= 0.9 else "similar"
            return best_match['answer'], match_type, best_score
        
        # Fallback
        fallback_answer = self.generate_fallback_response(user_question)
        return fallback_answer, "fallback", best_score
    
    def generate_fallback_response(self, question):
        """Génère une réponse de repli intelligente"""
        question_lower = question.lower()
        
        if any(mot in question_lower for mot in ['symptome', 'signe', 'detecter', 'remarquer']):
            return "Les signes du cancer du sein peuvent inclure : une boule dans le sein, un changement de forme ou de taille, un écoulement du mamelon, une rétraction de la peau. L'auto-examen mensuel aide à détecter ces changements précocement. En cas de doute, consultez un médecin. 💗"
        
        elif any(mot in question_lower for mot in ['traitement', 'soigner', 'guerir', 'therapie']):
            return "Le traitement du cancer du sein dépend du stade et peut inclure la chirurgie, la chimiothérapie, la radiothérapie ou l'hormonothérapie. Le dépistage précoce améliore considérablement les chances de guérison. 🏥"
        
        elif any(mot in question_lower for mot in ['prevention', 'eviter', 'proteger', 'risque']):
            return "Pour réduire les risques : pratiquez l'auto-examen mensuel, maintenez un poids santé, limitez l'alcool, allaitez si possible, et faites des mammographies régulières après 40 ans. La détection précoce sauve des vies ! 💪"
        
        else:
            return "Je n'ai pas trouvé d'information spécifique sur ce point dans ma base de données. Cependant, je vous encourage vivement à pratiquer l'auto-examen mensuel et à consulter un professionnel de santé pour toute question médicale. Votre santé est précieuse ! 💗"

# Instance globale avec détection automatique des capacités
try:
    rag_service = AdvancedRAGService()
    print("✅ Service RAG avancé initialisé")
except Exception as e:
    print(f"❌ Erreur initialisation RAG avancé: {e}")
    # Fallback vers le service basique
    from .rag_service_basic import RAGService
    rag_service = RAGService()







def convert_to_serializable(self, obj):
    """Convertit les objets non sérialisables en types Python natifs"""
    if hasattr(obj, 'item'):
        return obj.item()  # Pour numpy types
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {k: self.convert_to_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [self.convert_to_serializable(item) for item in obj]
    else:
        return obj

def find_best_match_advanced(self, user_question):
    """Nouvelle méthode de recherche avancée"""
    user_q_lower = user_question.lower().strip()
    
    # 1. SALUTATIONS
    salutations = ["bonjour", "salut", "coucou", "hello", "akwe", "yo", "bonsoir", "hi"]
    if any(salut == user_q_lower for salut in salutations):
        responses = [
            "Bonjour ! 😊 Je suis ANONTCHIGAN, votre assistante pour la sensibilisation au cancer du sein. Comment puis-je vous aider ?",
            "Salut ! 👋 Ravie de vous parler. Vous avez une question sur le cancer du sein ?",
            "Hello ! 💗 ANONTCHIGAN à votre service. Quelle est votre question ?"
        ]
        answer = random.choice(responses)
        return answer, "salutation", 1.0  # Retourne directement un float Python
    
    # 2. RECHERCHE PAR MOTS-CLÉS
    keyword_answer, keyword_score = self.find_by_keywords(user_q_lower)
    if keyword_answer and keyword_score >= 0.9:
        # Convertir le score en float Python
        keyword_score = float(keyword_score) if hasattr(keyword_score, 'item') else keyword_score
        return keyword_answer, "keyword_match", keyword_score
    
    # 3. RECHERCHE FAISS (si disponible)
    faiss_results = []
    if self.faiss_index:
        faiss_results = self.search_faiss(user_question, k=3)
    
    if not faiss_results:
        # Fallback vers la recherche par similarité basique
        return self.find_best_match_basic(user_question)
    
    best_result = faiss_results[0]
    similarity = best_result['similarity']
    
    # Convertir la similarité en float Python
    similarity = float(similarity) if hasattr(similarity, 'item') else similarity
    
    # 4. DÉCISION : JSON vs GÉNÉRATION
    SIMILARITY_THRESHOLD = 0.65
    
    if similarity >= SIMILARITY_THRESHOLD:
        # HAUTE SIMILARITÉ → Réponse directe du JSON
        return best_result['answer'], "json_direct", similarity
    
    else:
        # FAIBLE SIMILARITÉ → Génération avec Groq ou fallback
        context_parts = []
        for i, result in enumerate(faiss_results[:3], 1):
            answer_truncated = result['answer']
            if len(answer_truncated) > 250:
                answer_truncated = answer_truncated[:247] + "..."
            context_parts.append(f"{i}. Q: {result['question']}\n   R: {answer_truncated}")
        
        context = "\n\n".join(context_parts)
        generated_answer = self.generate_with_groq(user_question, context)
        
        return generated_answer, "groq_generated", similarity

def find_best_match_basic(self, user_question):
    """Méthode de fallback basique (sans FAISS)"""
    user_q_lower = user_question.lower().strip()
    
    # Recherche exacte
    for item in self.questions_data:
        if user_q_lower == item['question_normalisee']:
            return item['answer'], "exact", 1.0  # Float Python
    
    # Recherche par similarité
    best_match = None
    best_score = 0.0  # Déjà un float Python
    
    for item in self.questions_data:
        score = self.similarity_score(user_q_lower, item['question_normalisee'])
        if score > best_score:
            best_score = score
            best_match = item
    
    if best_match and best_score >= 0.6:
        match_type = "exact" if best_score >= 0.9 else "similar"
        return best_match['answer'], match_type, best_score  # best_score est déjà un float Python
    
    # Fallback
    fallback_answer = self.generate_fallback_response(user_question)
    return fallback_answer, "fallback", best_score