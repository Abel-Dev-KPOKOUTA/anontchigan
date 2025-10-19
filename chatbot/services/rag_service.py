import json
import os
import logging
from typing import Dict, List, Optional
import random

import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)


class Config:
    """Configuration du chatbot"""
    SIMILARITY_THRESHOLD = 0.75
    MAX_HISTORY_LENGTH = 8
    MAX_CONTEXT_LENGTH = 1000
    MAX_ANSWER_LENGTH = 600
    FAISS_RESULTS_COUNT = 3
    MIN_ANSWER_LENGTH = 30


class GroqService:
    """Service de génération avec Groq"""
    
    def __init__(self):
        self.client = None
        self.available = False
        self._initialize_groq()
    
    def _initialize_groq(self):
        try:
            from groq import Groq
            from django.conf import settings
            
            api_key = getattr(settings, 'GROQ_API_KEY', None)
            
            if not api_key:
                logger.warning("⚠️  Clé API Groq manquante dans settings.py")
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
            
        except ImportError:
            logger.warning("⚠️  Bibliothèque groq non installée")
        except Exception as e:
            logger.warning(f"⚠️  Service Groq non disponible: {str(e)}")
    
    def generate_response(self, question: str, context: str, history: List[Dict]) -> str:
        """Génère une réponse complète sans coupure"""
        if not self.available:
            raise RuntimeError("Service Groq non disponible")
        
        try:
            context_short = self._prepare_context(context)
            messages = self._prepare_messages(question, context_short, history)
            
            logger.info("🤖 Génération avec Groq...")
            
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                max_tokens=600,
                temperature=0.7,
                top_p=0.9,
            )
            
            answer = response.choices[0].message.content.strip()
            answer = self._clean_response(answer)
            
            if not self._is_valid_answer(answer):
                raise ValueError("Réponse trop courte")
                
            answer = self._ensure_complete_response(answer)
            
            logger.info(f"✓ Réponse générée ({len(answer)} caractères)")
            return answer
            
        except Exception as e:
            logger.error(f"❌ Erreur Groq: {str(e)}")
            raise
    
    def _prepare_context(self, context: str) -> str:
        lines = context.split('\n')[:5]
        context_short = '\n'.join(lines)
        if len(context_short) > Config.MAX_CONTEXT_LENGTH:
            context_short = context_short[:Config.MAX_CONTEXT_LENGTH-3] + "..."
        return context_short
    
















#     def _prepare_messages(self, question: str, context: str, history: List[Dict]) -> List[Dict]:
#         system_prompt = f"""Tu es ANONTCHIGAN, assistante IA professionnelle spécialisée dans la sensibilisation au cancer du sein au Bénin.

# CONTEXTE À UTILISER :
# {context}

# RÈGLES CRITIQUES :
# 1. FOURNIR DES RÉPONSES COMPLÈTES - ne JAMAIS couper une phrase
# 2. Si conseil de prévention, aller à la ligne AVANT
# 3. Terminer naturellement par un point final
# 4. TENIR COMPTE DE L'HISTORIQUE - Si référence à conversation précédente, utilise le contexte
# 5. CONTINUITÉ - "et ça ?", "pourquoi ?", "explique mieux" = se baser sur la discussion

# STYLE :
# - Professionnel, clair, empathique
# - Réponses directes sans formules introductives répétitives
# - CONCIS mais COMPLET
# - Emojis : 💗 🌸 😊 🇧🇯

# STRUCTURE :
# 1. Réponse basée sur contexte ET historique
# 2. N'invente PAS d'informations
# 3. Si contexte incomplet, recommande consultation professionnelle
# 4. ENSGMM = École Nationale Supérieure de Génie Mathématique et Modélisation

# HISTORIQUE :
# - Utilise l'historique pour comprendre le contexte complet
# - Questions de suivi : réfère-toi aux échanges précédents
# - Maintiens la cohérence

# ANTI-COUPURE :
# - Vérifie que ta réponse est complète
# - Ne coupe PAS en milieu de phrase
# - Termine par un point final"""

#         messages = [{"role": "system", "content": system_prompt}]
        
#         # Inclure historique récent
#         history_to_include = history[-6:] if len(history) > 6 else history
#         for msg in history_to_include:
#             messages.append(msg)
        
#         messages.append({
#             "role": "user", 
#             "content": f"QUESTION: {question}\n\nRéponds de façon COMPLÈTE. Tiens compte de notre conversation si pertinent."
#         })
        
#         return messages
    



    def _prepare_messages(self, question: str, context: str, history: List[Dict]) -> List[Dict]:
        system_prompt = f"""Tu es ANONTCHIGAN, assistante IA professionnelle spécialisée dans la sensibilisation au cancer du sein au Bénin.

    CONTEXTE À UTILISER :
    {context}

    
    RÈGLES CRITIQUES :
    1. FOURNIR DES RÉPONSES COMPLÈTES - ne JAMAIS couper une phrase
    2. Si conseil de prévention, aller à la ligne AVANT
    3. Terminer naturellement par un point final
    4. TENIR COMPTE DE L'HISTORIQUE - Si référence à conversation précédente, utilise le contexte
    5. CONTINUITÉ - "et ça ?", "pourquoi ?", "explique mieux" = se baser sur la discussion

    STYLE :
    - Professionnel, clair, empathique
    - Réponses directes sans formules introductives répétitives
    - CONCIS mais COMPLET
    - Emojis : 💗 🌸 😊 🇧🇯
    - **EXPRESSIONS CULTURELLES : Utilise "Atassa!" ou "Atassaaaaa!" en début de phrase pour l'humour et l'étonnement extrême**
    - **TON : Chaleureux et authentique comme une conversation entre amies**

    STRUCTURE :
    1. Réponse basée sur contexte ET historique
    2. N'invente PAS d'informations
    3. Si contexte incomplet, recommande consultation professionnelle
    4. ENSGMM = École Nationale Supérieure de Génie Mathématique et Modélisation

    HISTORIQUE :
    - Utilise l'historique pour comprendre le contexte complet
    - Questions de suivi : réfère-toi aux échanges précédents
    - Maintiens la cohérence

    EXPRESSIONS ET TON :
    - **Atassa!** : Pour exprimer l'étonnement positif ("Atassa! Cette question est excellente !")
    - **Atassaaaaa!** : Pour l'humour ou l'étonnement extrême ("Atassaaaaa! Tu poses des questions très pointues !")
    - **Ton chaleureux** : Comme si tu parlais à une amie, mais avec professionnalisme
    - **Équilibre** : 1 expression "Atassa" toutes les 3-4 réponses pour garder l'authenticité sans exagération

    ANTI-COUPURE :
    - Vérifie que ta réponse est complète
    - Ne coupe PAS en milieu de phrase
    - Termine par un point final"""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Inclure historique récent
        history_to_include = history[-6:] if len(history) > 6 else history
        for msg in history_to_include:
            messages.append(msg)
        
        messages.append({
            "role": "user", 
            "content": f"QUESTION: {question}\n\nRéponds de façon COMPLÈTE. Tiens compte de notre conversation si pertinent. Utilise 'Atassa!' si approprié pour l'humour ou l'étonnement."
        })
        
        return messages

    
    def _clean_response(self, answer: str) -> str:
        unwanted_intros = [
            'bonjour', 'salut', 'coucou', 'hello', 'akwè', 'yo', 'bonsoir', 'hi',
            'excellente question', 'je suis ravi', 'permettez-moi'
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
        return (len(answer) >= Config.MIN_ANSWER_LENGTH and 
                not answer.lower().startswith(('je ne sais pas', 'désolé')))
    
    def _ensure_complete_response(self, answer: str) -> str:
        if not answer:
            return answer
            
        cut_indicators = [
            answer.endswith('...'),
            answer.endswith(','),
            answer.endswith(';'),
            '...' in answer[-10:]
        ]
        
        if any(cut_indicators):
            logger.warning("⚠️  Détection possible de réponse coupée")
            
            last_period = answer.rfind('.')
            last_exclamation = answer.rfind('!')
            last_question = answer.rfind('?')
            
            sentence_end = max(last_period, last_exclamation, last_question)
            
            if sentence_end > 0 and sentence_end >= len(answer) - 5:
                answer = answer[:sentence_end + 1]
            else:
                answer = answer.rstrip(' ,;...')
                if not answer.endswith(('.', '!', '?')):
                    answer += '.'
        
        return answer


class RAGService:
    """Service RAG avec FAISS"""
    
    def __init__(self):
        from django.conf import settings
        
        self.questions_data = []
        self.embedding_model = None
        self.index = None
        self.embeddings = None
        
        data_path = os.path.join(settings.BASE_DIR, 'chatbot', 'data', 'cancer_sein.json')
        self._load_data(data_path)
        self._initialize_embeddings()
    
    def _load_data(self, data_file: str):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for item in data:
                self.questions_data.append({
                    'question_originale': item['question'],
                    'question_normalisee': item['question'].lower().strip(),
                    'answer': item['answer']
                })
            
            logger.info(f"✓ {len(self.questions_data)} questions chargées")
            
        except Exception as e:
            logger.error(f"❌ Erreur chargement données: {str(e)}")
            raise
    
    def _initialize_embeddings(self):
        try:
            self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
            
            all_texts = [
                f"Q: {item['question_originale']} R: {item['answer']}"
                for item in self.questions_data
            ]
            
            self.embeddings = self.embedding_model.encode(all_texts, show_progress_bar=False)
            self.embeddings = np.array(self.embeddings).astype('float32')
            
            dimension = self.embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(self.embeddings)
            
            logger.info(f"✓ Index FAISS créé ({len(self.embeddings)} vecteurs)")
            
        except Exception as e:
            logger.error(f"❌ Erreur initialisation embeddings: {str(e)}")
            raise
    
    def search(self, query: str, k: int = Config.FAISS_RESULTS_COUNT) -> List[Dict]:
        try:
            query_embedding = self.embedding_model.encode([query])
            query_embedding = np.array(query_embedding).astype('float32')
            
            distances, indices = self.index.search(query_embedding, k)
            
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
            logger.error(f"❌ Erreur recherche FAISS: {str(e)}")
            return []


class ConversationManager:
    """Gestionnaire de conversations"""
    
    def __init__(self):
        self.conversations: Dict[str, List[Dict]] = {}
    
    def get_history(self, user_id: str) -> List[Dict]:
        return self.conversations.get(user_id, [])
    
    def add_message(self, user_id: str, role: str, content: str):
        if user_id not in self.conversations:
            self.conversations[user_id] = []
        
        self.conversations[user_id].append({"role": role, "content": content})
        
        if len(self.conversations[user_id]) > Config.MAX_HISTORY_LENGTH * 2:
            self.conversations[user_id] = self.conversations[user_id][-Config.MAX_HISTORY_LENGTH * 2:]








class ChatbotService:
    """Service principal du chatbot"""
    
    def __init__(self):
        self.groq_service = GroqService()
        self.rag_service = RAGService()
        self.conversation_manager = ConversationManager()
        logger.info("✓ ChatbotService initialisé")
    
    def process_question(self, question: str, user_id: str) -> Dict:
        """Traite une question et retourne une réponse"""
        
        try:
            history = self.conversation_manager.get_history(user_id)
            logger.info(f"📜 Historique utilisateur {user_id}: {len(history)} messages")
            
            # Gestion des salutations
            salutations = ["cc", "bonjour", "salut", "coucou", "hello", "akwe", "yo", "bonsoir", "hi"]
            question_lower = question.lower().strip()
            
            if any(salut == question_lower for salut in salutations) and len(history) == 0:
                responses = [
                    "Je suis ANONTCHIGAN, assistante pour la sensibilisation au cancer du sein. Comment puis-je vous aider ? 💗",
                    "Bonjour ! Je suis ANONTCHIGAN. Que souhaitez-vous savoir sur le cancer du sein ? 🌸",
                    "ANONTCHIGAN à votre service. Posez-moi vos questions sur la prévention du cancer du sein. 😊"
                ]
                answer = random.choice(responses)
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", answer)
                
                return {'answer': answer, 'method': 'salutation'}
            
            if any(salut == question_lower for salut in salutations) and len(history) > 0:
                answer = "Je suis toujours là ! 😊 Continuons notre discussion sur la santé mammaire. Que voulez-vous savoir ?"
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", answer)
                
                return {'answer': answer, 'method': 'salutation_continue'}
            
            # Recherche FAISS
            faiss_results = self.rag_service.search(question)
            
            # Détecter question de suivi
            is_followup = self._is_followup_question(question, history)
            
            if is_followup and len(history) > 0:
                logger.info("🔗 Question de suivi détectée - priorité à l'historique")
                
                context_parts = []
                recent_history = history[-4:] if len(history) > 4 else history
                for i, msg in enumerate(recent_history):
                    if msg['role'] == 'assistant':
                        context_parts.append(f"Message précédent {i+1}: {msg['content'][:200]}")
                
                for i, result in enumerate(faiss_results[:2], 1):
                    answer_truncated = result['answer']
                    if len(answer_truncated) > 200:
                        answer_truncated = answer_truncated[:197] + "..."
                    context_parts.append(f"{i}. Q: {result['question']}\n   R: {answer_truncated}")
                
                context = "\n\n".join(context_parts)
                
                try:
                    if self.groq_service.available:
                        generated_answer = self.groq_service.generate_response(question, context, history)
                    else:
                        generated_answer = "Je me base sur notre discussion précédente, mais pour plus de détails, consultez un professionnel. 💗"
                except Exception as e:
                    logger.warning(f"Génération échouée: {str(e)}")
                    generated_answer = "Pour continuer cette discussion, consultez un médecin spécialisé. 🌸"
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", generated_answer)
                
                return {
                    'answer': generated_answer,
                    'method': 'followup_generated',
                    'score': None
                }
            
            if not faiss_results:
                answer = "Les informations disponibles ne couvrent pas ce point. Je vous recommande de consulter un professionnel de santé au Bénin. 💗"
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", answer)
                
                return {'answer': answer, 'method': 'no_result'}
            
            best_result = faiss_results[0]
            similarity = best_result['similarity']
            
            if similarity >= Config.SIMILARITY_THRESHOLD:
                answer = best_result['answer']
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", answer)
                
                return {
                    'answer': answer,
                    'method': 'direct',
                    'score': float(similarity),
                    'matched_question': best_result['question']
                }
            else:
                context_parts = []
                for i, result in enumerate(faiss_results[:3], 1):
                    answer_truncated = result['answer']
                    if len(answer_truncated) > 200:
                        answer_truncated = answer_truncated[:197] + "..."
                    context_parts.append(f"{i}. Q: {result['question']}\n   R: {answer_truncated}")
                
                context = "\n\n".join(context_parts)
                
                try:
                    if self.groq_service.available:
                        generated_answer = self.groq_service.generate_response(question, context, history)
                    else:
                        generated_answer = "Pour cette question, consultez un professionnel de santé. La prévention précoce est essentielle. 💗"
                except Exception as e:
                    logger.warning(f"Génération échouée: {str(e)}")
                    generated_answer = "Pour des informations précises, consultez un médecin spécialisé au Bénin. 🌸"
                
                self.conversation_manager.add_message(user_id, "user", question)
                self.conversation_manager.add_message(user_id, "assistant", generated_answer)
                
                return {
                    'answer': generated_answer,
                    'method': 'generated',
                    'score': float(similarity)
                }
                
        except Exception as e:
            logger.error(f"❌ Erreur: {str(e)}")
            return {
                'answer': "Désolé, une erreur s'est produite. Veuillez réessayer.",
                'method': 'error'
            }
    
    def get_health_status(self) -> Dict:
        """Retourne l'état de santé du service"""
        return {
            'groq_available': self.groq_service.available,
            'questions_count': len(self.rag_service.questions_data)
        }
    
    def _is_followup_question(self, question: str, history: List[Dict]) -> bool:
        """Détecte si la question fait référence à la conversation précédente"""
        if len(history) == 0:
            return False
        
        followup_keywords = [
            'ça', 'cela', 'celui', 'celle', 'ceux', 'celles',
            'pourquoi', 'comment', 'quand', 'où', 'combien',
            'explique', 'détaille', 'précise', 'développe',
            'tu as dit', 'tu disais', 'tu parlais', 'tu mentionnais',
            'avant', 'précédemment', 'plus tôt', 'tantôt',
            'je comprends pas', 'je ne comprends pas', 'pas clair',
            'et', 'mais', 'donc', 'alors', 'aussi', 'encore',
            'il', 'elle', 'ils', 'elles', 'le', 'la', 'les',
        ]
        
        question_lower = question.lower()
        
        # Question très courte
        if len(question.split()) <= 3:
            return True
        
        # Commence par mot-clé
        for keyword in followup_keywords:
            if question_lower.startswith(keyword):
                return True
        
        # Plusieurs mots-clés
        keyword_count = sum(1 for kw in followup_keywords if kw in question_lower)
        if keyword_count >= 2:
            return True
        
        return False


    

