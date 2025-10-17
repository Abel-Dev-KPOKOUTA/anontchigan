import json
import os
import logging
import random
import numpy as np
from difflib import SequenceMatcher
from django.conf import settings
from typing import Dict, List  # ← AJOUTEZ CETTE LIGNE

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("ANONTCHIGAN")

class Config:
    """Configuration optimisée pour éviter les coupures"""
    SIMILARITY_THRESHOLD = 0.75
    MAX_HISTORY_LENGTH = 8
    MAX_CONTEXT_LENGTH = 1000
    MAX_ANSWER_LENGTH = 600
    FAISS_RESULTS_COUNT = 3
    MIN_ANSWER_LENGTH = 30

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

class GroqService:
    
    def __init__(self):
        self.client = None
        self.available = False
        self._initialize_groq()
    
    def _initialize_groq(self):
        try:
            from groq import Groq
            
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            if not api_key:
                logger.warning("Clé API Groq manquante")
                return
            
            self.client = Groq(api_key=api_key)
            
            # Test de connexion
            self.client.chat.completions.create(
                messages=[{"role": "user", "content": "test"}],
                model="llama-3.1-8b-instant",
                max_tokens=5,
            )
            self.available = True
            logger.info("✓ Service Groq initialisé")
            
        except Exception as e:
            logger.warning(f"Service Groq non disponible: {str(e)}")
    
    def generate_response(self, question: str, context: str) -> str:
        """Génère une réponse complète sans coupure (version adaptée)"""
        if not self.available:
            raise RuntimeError("Service Groq non disponible")
        
        try:
            # Préparer le contexte optimisé
            context_short = self._prepare_context(context)
            
            # Préparer les messages
            messages = self._prepare_messages(question, context_short)
            
            logger.info("🤖 Génération avec Groq...")
            
            # AUGMENTER SIGNIFICATIVEMENT les tokens pour éviter les coupures
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=600,  # Augmenté pour éviter coupures
                temperature=0.7,
                top_p=0.9,
            )
            
            answer = response.choices[0].message.content.strip()
            answer = self._clean_response(answer)
            
            # Validation renforcée
            if not self._is_valid_answer(answer):
                raise ValueError("Réponse trop courte")
                
            # Vérification et correction des coupures
            answer = self._ensure_complete_response(answer)
            
            logger.info(f"✓ Réponse générée ({len(answer)} caractères)")
            return answer
            
        except Exception as e:
            logger.error(f"Erreur Groq: {str(e)}")
            raise
    
    def _prepare_context(self, context: str) -> str:
        """Prépare un contexte concis"""
        lines = context.split('\n')[:5]
        context_short = '\n'.join(lines)
        if len(context_short) > Config.MAX_CONTEXT_LENGTH:
            context_short = context_short[:Config.MAX_CONTEXT_LENGTH-3] + "..."
        return context_short
    
    def _prepare_messages(self, question: str, context: str) -> List[Dict]:
        """Prépare les messages avec instructions claires contre les coupures"""
        
        system_prompt = f"""Tu es ANONTCHIGAN, assistante IA professionnelle spécialisée dans la sensibilisation au cancer du sein au Bénin.

CONTEXTE À UTILISER :
{context}

RÈGLES CRITIQUES :
1. FOURNIR DES RÉPONSES COMPLÈTES - ne JAMAIS couper une phrase en milieu de mot
2. Si tu donnes un conseil de prévention, aller deux fois à la ligne AVANT de le donner
3. Tes réponses doivent se terminer naturellement par un point final

STYLE :
- Professionnel, clair, empathique
- Réponses directes sans formules introductives
- CONCIS mais COMPLET
- Humour humain léger 1 fois sur 3 réponses
- Emojis à utiliser fréquemment : 💗 🌸 😊 🇧🇯

STRUCTURE DES RÉPONSES :
1. Réponse principale basée sur le contexte
2. N'invente PAS d'informations
3. Si le contexte ne couvre pas la question, recommande de consulter un professionnel de santé au Bénin
4. ENSGMM se définit comme l'Ecole Nationale Supérieure de Génie Mathématique et Modélisation 
5. Utilise des connecteurs logiques pour fluidifier et produire des réponses naturelles et cohérentes

INFORMATIONS SUR LES CRÉATEURS (UNIQUEMENT SI DANS LE CONTEXTE) :
- Judicaël Karol DOBOEVI
- Hornel Ursus GBAGUIDI  
- Abel Kocou KPOKOUTA
- Josaphat ADJELE
- Club IA de l'ENSGMM (École Nationale Supérieure de Génie Mathématique et Modélisation)


INTERDICTIONS STRICTES :
- N'ajoute PAS d'autres noms de créateurs/collaborateurs
- N'invente PAS d'institutions partenaires


DIRECTIVES ANTI-COUPURE :
- Vérifie que ta réponse est complète avant de terminer
- Ne coupe PAS en milieu de phrase ou de mot
- Utilise "Atassa!" ou "Atassaaaaa!" en debut de phrase en cas d'humour et d'étonnement extrême
- Termine par un point final approprié
- Si tu mentionnes des noms (créateurs, etc.), assure-toi qu'ils sont COMPLETS

Conseils de prévention : seulement si pertinents et si demandés."""

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user", 
                "content": f"QUESTION: {question}\n\nIMPORTANT : Réponds de façon COMPLÈTE sans couper ta réponse. Termine par un point final. Si conseil de prévention, va à la ligne avant."
            }
        ]
        
        return messages
    
    def _clean_response(self, answer: str) -> str:
        """Nettoie la réponse en gardant la personnalité"""
        
        # Supprimer les introductions verbeuses
        unwanted_intros = [
            'bonjour', 'salut', 'coucou', 'hello', 'akwè', 'yo', 'bonsoir', 'hi',
            'excellente question', 'je suis ravi', 'permettez-moi', 'tout d abord',
            'premièrement', 'pour commencer', 'en tant qu', 'je suis anontchigan'
        ]
        
        answer_lower = answer.lower()
        for phrase in unwanted_intros:
            if answer_lower.startswith(phrase):
                sentences = answer.split('.')
                if len(sentences) > 1:
                    answer = '.'.join(sentences[1:]).strip()
                    if answer:
                        answer = answer[0].upper() + answer[1:]
                break
        
        return answer.strip()
    
    def _is_valid_answer(self, answer: str) -> bool:
        """Valide que la réponse est acceptable"""
        return (len(answer) >= Config.MIN_ANSWER_LENGTH and 
                not answer.lower().startswith(('je ne sais pas', 'désolé', 'sorry')))
    
    def _ensure_complete_response(self, answer: str) -> str:
        """Garantit que la réponse est complète et non coupée"""
        if not answer:
            return answer
            
        # Détecter les signes de coupure
        cut_indicators = [
            answer.endswith('...'),
            answer.endswith(','),
            answer.endswith(';'),
            answer.endswith(' '),
            any(word in answer.lower() for word in ['http', 'www.', '.com']),
            '...' in answer[-10:]
        ]
        
        if any(cut_indicators):
            logger.warning("⚠️  Détection possible de réponse coupée")
            
            # Trouver la dernière phrase complète
            last_period = answer.rfind('.')
            last_exclamation = answer.rfind('!')
            last_question = answer.rfind('?')
            
            sentence_end = max(last_period, last_exclamation, last_question)
            
            if sentence_end > 0 and sentence_end >= len(answer) - 5:
                # Garder jusqu'à la dernière phrase complète
                answer = answer[:sentence_end + 1]
            else:
                # Si pas de ponctuation claire, nettoyer la fin
                answer = answer.rstrip(' ,;...')
                if not answer.endswith(('.', '!', '?')):
                    answer += '.'
        
        # Formater les conseils de prévention avec saut de ligne
        prevention_phrases = [
            'conseil de prévention',
            'pour prévenir',
            'je recommande',
            'il est important de',
            'n oubliez pas de'
        ]
        
        # Vérifier si un conseil de prévention est présent
        has_prevention_advice = any(phrase in answer.lower() for phrase in prevention_phrases)
        
        if has_prevention_advice:
            # Essayer d'insérer un saut de ligne avant le conseil
            lines = answer.split('. ')
            if len(lines) > 1:
                # Trouver la ligne qui contient le conseil
                for i, line in enumerate(lines[1:], 1):
                    if any(phrase in line.lower() for phrase in prevention_phrases):
                        # Insérer un saut de ligne avant cette ligne
                        lines[i] = '\n' + lines[i]
                        answer = '. '.join(lines)
                        break
        
        return answer

class AdvancedRAGService:
    def __init__(self):
        self.questions_data = []
        self.embedding_model = None
        self.faiss_index = None
        self.groq_service = GroqService()
        
        self.load_data()
        self.initialize_advanced_features()
    
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
            
            logger.info(f"✅ {len(self.questions_data)} questions chargées")
            
        except FileNotFoundError:
            logger.error("❌ Fichier cancer_sein.json non trouvé")
        except Exception as e:
            logger.error(f"❌ Erreur chargement RAG: {e}")
    
    def initialize_advanced_features(self):
        """Initialise FAISS et les embeddings si disponibles"""
        if not HAS_ADVANCED_DEPS:
            logger.info("⚠️ Mode basique - FAISS non disponible")
            return
        
        try:
            logger.info("🔍 Initialisation des embeddings...")
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            logger.info("📊 Création de l'index FAISS...")
            embeddings = self.embedding_model.encode(self.all_texts, show_progress_bar=False)
            embeddings = np.array(embeddings).astype('float32')
            
            dimension = embeddings.shape[1]
            self.faiss_index = faiss.IndexFlatL2(dimension)
            self.faiss_index.add(embeddings)
            
            logger.info(f"✓ Index FAISS créé ({len(embeddings)} vecteurs, dim={dimension})")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation FAISS: {e}")
            self.embedding_model = None
            self.faiss_index = None
    
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
            logger.error(f"❌ Erreur recherche FAISS: {e}")
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
        """Génère une réponse avec Groq (version améliorée anti-coupure)"""
        if not self.groq_service.available:
            return self.generate_fallback_from_context(context)
        
        try:
            return self.groq_service.generate_response(question, context)
        except Exception as e:
            logger.error(f"❌ Erreur Groq: {e}")
            return self.generate_fallback_from_context(context)
    
    def find_best_match_advanced(self, user_question):
        """Nouvelle méthode de recherche avancée avec anti-coupure"""
        user_q_lower = user_question.lower().strip()
        
        # 1. SALUTATIONS
        salutations = ["cc","bonjour", "salut", "coucou", "hello", "akwe", "yo", "bonsoir", "hi"]
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
        if similarity >= Config.SIMILARITY_THRESHOLD:
            # HAUTE SIMILARITÉ → Réponse directe du JSON
            answer = best_result['answer']
            
            # S'assurer que les réponses directes ne sont pas coupées
            if len(answer) > Config.MAX_ANSWER_LENGTH:
                answer = answer[:Config.MAX_ANSWER_LENGTH-3] + "..."
            
            return answer, "json_direct", similarity
        
        else:
            # FAIBLE SIMILARITÉ → Génération avec Groq ou fallback
            context_parts = []
            for i, result in enumerate(faiss_results[:3], 1):
                answer_truncated = result['answer']
                if len(answer_truncated) > 200:
                    answer_truncated = answer_truncated[:197] + "..."
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

# Instance globale
try:
    rag_service = AdvancedRAGService()
    logger.info("✅ Service RAG avancé avec anti-coupure initialisé")
except Exception as e:
    logger.error(f"❌ Erreur initialisation RAG avancé: {e}")
    rag_service = None