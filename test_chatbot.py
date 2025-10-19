#!/usr/bin/env python
"""
TEST COMPLET DU SYSTÈME DE MÉMOIRE CONTEXTUELLE
Script de test complet pour vérifier le système de mémoire contextuelle du chatbot ANONTCHIGAN
"""
import os
import sys
import time
import uuid
import django
from datetime import datetime

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anontchigan.settings')
django.setup()

from chatbot.services.rag_service import ChatbotService, Config

class TestLogger:
    """Logger personnalisé pour les tests"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
    
    def print_separator(self, title=None, length=70):
        """Affiche un séparateur avec titre optionnel"""
        if title:
            print(f"\n{title}")
            print("=" * length)
        else:
            print("\n" + "=" * length)
    
    def print_step(self, message):
        """Affiche une étape de test"""
        print(f"\n📋 {message}")
        print("-" * 50)
    
    def print_success(self, message):
        """Affiche un succès"""
        print(f"✅ {message}")
        self.passed_count += 1
    
    def print_warning(self, message):
        """Affiche un avertissement"""
        print(f"⚠️  {message}")
    
    def print_error(self, message):
        """Affiche une erreur"""
        print(f"❌ {message}")
        self.failed_count += 1
    
    def print_info(self, message):
        """Affiche une information"""
        print(f"ℹ️  {message}")
    
    def print_result(self, test_name, success, details=None):
        """Affiche le résultat d'un test"""
        self.test_count += 1
        if success:
            self.print_success(f"{test_name}")
        else:
            self.print_error(f"{test_name}")
        
        if details:
            print(f"   📝 {details}")
    
    def get_summary(self):
        """Retourne le résumé des tests"""
        duration = datetime.now() - self.start_time
        return {
            'total_tests': self.test_count,
            'passed': self.passed_count,
            'failed': self.failed_count,
            'success_rate': (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0,
            'duration': duration
        }


class ComprehensiveContextMemoryTest:
    """Classe principale de test du système de mémoire contextuelle"""
    
    def __init__(self):
        self.logger = TestLogger()
        self.service = None
        self.setup_completed = False
    
    def setup(self):
        """Initialise l'environnement de test"""
        self.logger.print_separator("🧪 INITIALISATION DU SYSTÈME DE TEST")
        
        try:
            self.logger.print_step("Chargement du service chatbot...")
            self.service = ChatbotService()
            
            # Vérifier l'état du service
            health_status = self.service.get_health_status()
            self.logger.print_info(f"État du service: {health_status}")
            
            if not health_status['groq_available']:
                self.logger.print_warning("Service Groq non disponible - certains tests utiliseront le fallback")
            
            self.logger.print_success("Service chatbot initialisé avec succès")
            self.setup_completed = True
            
        except Exception as e:
            self.logger.print_error(f"Échec de l'initialisation: {e}")
            raise
    
    def test_basic_conversation_flow(self):
        """Test le flux de conversation basique avec contexte"""
        self.logger.print_separator("🧪 TEST 1: FLUX DE CONVERSATION BASIQUE")
        
        user_id = f"test_basic_{uuid.uuid4().hex[:8]}"
        success = True
        details = []
        
        try:
            # Test 1.1: Première question
            self.logger.print_step("Test 1.1 - Première question")
            question1 = "Comment faire un auto-examen du sein ?"
            response1 = self.service.process_question(question1, user_id)
            
            history = self.service.conversation_manager.get_history(user_id)
            if len(history) == 2:
                self.logger.print_success("Historique initial créé correctement")
            else:
                self.logger.print_error(f"Historique incorrect: {len(history)} messages au lieu de 2")
                success = False
                details.append("Échec création historique")
            
            # Test 1.2: Question de suivi directe
            self.logger.print_step("Test 1.2 - Question de suivi directe")
            question2 = "Pourquoi c'est important ?"
            is_followup = self.service._is_followup_question(question2, history)
            
            if is_followup:
                self.logger.print_success("Détection de suivi correcte")
            else:
                self.logger.print_error("Échec détection de suivi")
                success = False
                details.append("Détection suivi échouée")
            
            response2 = self.service.process_question(question2, user_id)
            history = self.service.conversation_manager.get_history(user_id)
            
            if len(history) == 4:
                self.logger.print_success("Historique mis à jour correctement")
            else:
                self.logger.print_error(f"Historique incorrect après suivi: {len(history)} messages")
                success = False
                details.append("Mise à jour historique échouée")
            
            # Test 1.3: Question avec référence contextuelle
            self.logger.print_step("Test 1.3 - Référence contextuelle")
            question3 = "Et pour les jeunes filles, c'est pareil ?"
            response3 = self.service.process_question(question3, user_id)
            
            # Vérifier que la réponse fait référence au contexte
            answer_lower = response3['answer'].lower()
            context_indicators = ['auto-examen', 'sein', 'jeune', 'fille', 'adolescente']
            context_used = any(indicator in answer_lower for indicator in context_indicators)
            
            if context_used:
                self.logger.print_success("Contexte utilisé dans la réponse")
            else:
                self.logger.print_warning("Contexte potentiellement sous-utilisé")
                details.append("Contexte sous-utilisé")
            
            self.logger.print_result("Flux de conversation basique", success, "; ".join(details) if details else None)
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            success = False
            self.logger.print_result("Flux de conversation basique", False, f"Erreur: {e}")
        
        return success
    
    def test_followup_detection_accuracy(self):
        """Test la précision de la détection des questions de suivi"""
        self.logger.print_separator("🧪 TEST 2: PRÉCISION DE DÉTECTION DES SUIVIS")
        
        try:
            # Historique simulé
            fake_history = [
                {"role": "user", "content": "Comment faire l'auto-examen du sein ?"},
                {"role": "assistant", "content": "Voici comment procéder..."}
            ]
            
            test_cases = [
                # (question, attendu, raison)
                ("Pourquoi ?", True, "Question courte + mot-clé"),
                ("Et ça ?", True, "Question très courte"),
                ("Comment ?", True, "Question courte + mot-clé"),
                ("Explique mieux", True, "Mot-clé 'explique'"),
                ("Tu as dit quoi avant ?", True, "Référence au passé"),
                ("C'est quoi les symptômes ?", False, "Question indépendante"),
                ("Il faut le faire quand ?", True, "Pronom + contexte"),
                ("Quels sont les facteurs de risque du cancer ?", False, "Nouveau sujet"),
                ("", False, "Question vide"),
                ("   ", False, "Espaces seulement"),
            ]
            
            correct_detections = 0
            total_cases = len(test_cases)
            details = []
            
            for question, expected, reason in test_cases:
                result = self.service._is_followup_question(question, fake_history)
                status = result == expected
                
                if status:
                    correct_detections += 1
                    self.logger.print_success(f"'{question}' → {result} ({reason})")
                else:
                    self.logger.print_error(f"'{question}' → Attendu: {expected}, Obtenu: {result}")
                    details.append(f"'{question}': attendu {expected}, obtenu {result}")
            
            accuracy = correct_detections / total_cases * 100
            success = accuracy >= 80  # Seuil de 80% de précision
            
            if success:
                self.logger.print_success(f"Précision: {accuracy:.1f}% ({correct_detections}/{total_cases})")
            else:
                self.logger.print_error(f"Précision: {accuracy:.1f}% ({correct_detections}/{total_cases})")
            
            self.logger.print_result(
                "Détection des questions de suivi", 
                success, 
                f"Précision: {accuracy:.1f}%" + ("; " + "; ".join(details) if details else "")
            )
            
            return success
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            self.logger.print_result("Détection des questions de suivi", False, f"Erreur: {e}")
            return False
    
    def test_history_management(self):
        """Test la gestion de l'historique (limites, conservation)"""
        self.logger.print_separator("🧪 TEST 3: GESTION DE L'HISTORIQUE")
        
        user_id = f"test_history_{uuid.uuid4().hex[:8]}"
        success = True
        details = []
        
        try:
            # Test 3.1: Ajout de messages jusqu'à la limite
            self.logger.print_step("Test 3.1 - Limite d'historique")
            
            # Ajouter plus de messages que la limite
            excess_messages = Config.MAX_HISTORY_LENGTH * 2 + 5
            
            for i in range(excess_messages):
                self.service.conversation_manager.add_message(user_id, "user", f"Message utilisateur {i}")
                self.service.conversation_manager.add_message(user_id, "assistant", f"Réponse assistant {i}")
            
            history = self.service.conversation_manager.get_history(user_id)
            max_expected = Config.MAX_HISTORY_LENGTH * 2
            
            if len(history) <= max_expected:
                self.logger.print_success(f"Limite respectée: {len(history)}/{max_expected} messages")
            else:
                self.logger.print_error(f"Limite dépassée: {len(history)}/{max_expected} messages")
                success = False
                details.append("Limite historique dépassée")
            
            # Test 3.2: Conservation des messages récents
            self.logger.print_step("Test 3.2 - Conservation des messages récents")
            
            if history and "Réponse assistant" in history[-1]['content']:
                self.logger.print_success("Messages récents conservés")
            else:
                self.logger.print_error("Messages récents non conservés")
                success = False
                details.append("Conservation messages échouée")
            
            # Test 3.3: Isolation des sessions
            self.logger.print_step("Test 3.3 - Isolation des sessions utilisateur")
            
            other_user_id = f"other_user_{uuid.uuid4().hex[:8]}"
            self.service.conversation_manager.add_message(other_user_id, "user", "Question autre utilisateur")
            
            history_other = self.service.conversation_manager.get_history(other_user_id)
            history_original = self.service.conversation_manager.get_history(user_id)
            
            if len(history_other) == 1 and len(history_original) > 1:
                self.logger.print_success("Sessions utilisateur isolées")
            else:
                self.logger.print_error("Problème d'isolation des sessions")
                success = False
                details.append("Isolation sessions échouée")
            
            self.logger.print_result("Gestion de l'historique", success, "; ".join(details) if details else None)
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            success = False
            self.logger.print_result("Gestion de l'historique", False, f"Erreur: {e}")
        
        return success
    
    def test_contextual_understanding(self):
        """Test la compréhension contextuelle avancée"""
        self.logger.print_separator("🧪 TEST 4: COMPRÉHENSION CONTEXTUELLE")
        
        user_id = f"test_context_{uuid.uuid4().hex[:8]}"
        success = True
        details = []
        
        try:
            # Test 4.1: Conversation cohérente sur un sujet
            self.logger.print_step("Test 4.1 - Cohérence thématique")
            
            questions = [
                "Qu'est-ce que le cancer du sein ?",
                "Quels en sont les symptômes principaux ?", 
                "Comment les détecter précocement ?",
                "À partir de quel âge faut-il être vigilant ?"
            ]
            
            responses = []
            for question in questions:
                response = self.service.process_question(question, user_id)
                responses.append(response)
            
            # Vérifier que les réponses sont cohérentes
            breast_cancer_terms = ['sein', 'cancer', 'mammaire', 'tumeur']
            thematic_coherence = all(
                any(term in response['answer'].lower() for term in breast_cancer_terms)
                for response in responses
            )
            
            if thematic_coherence:
                self.logger.print_success("Cohérence thématique maintenue")
            else:
                self.logger.print_warning("Cohérence thématique partielle")
                details.append("Cohérence thématique partielle")
            
            # Test 4.2: Références croisées
            self.logger.print_step("Test 4.2 - Références croisées")
            
            followup_question = "Et pour les hommes, ces symptômes sont-ils les mêmes ?"
            followup_response = self.service.process_question(followup_question, user_id)
            
            # Vérifier que la réponse fait référence au contexte des symptômes
            answer_lower = followup_response['answer'].lower()
            context_references = ['symptôme', 'homme', 'masculin', 'cancer']
            context_used = sum(1 for ref in context_references if ref in answer_lower)
            
            if context_used >= 2:
                self.logger.print_success("Références contextuelles détectées")
            else:
                self.logger.print_warning("Peu de références contextuelles")
                details.append("Références contextuelles limitées")
            
            self.logger.print_result("Compréhension contextuelle", success, "; ".join(details) if details else None)
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            success = False
            self.logger.print_result("Compréhension contextuelle", False, f"Erreur: {e}")
        
        return success
    
    def test_performance_and_scalability(self):
        """Test les performances et l'évolutivité du système"""
        self.logger.print_separator("🧪 TEST 5: PERFORMANCE ET ÉVOLUTIVITÉ")
        
        success = True
        details = []
        
        try:
            # Test 5.1: Performance avec multiples utilisateurs
            self.logger.print_step("Test 5.1 - Performance multi-utilisateurs")
            
            start_time = time.time()
            user_count = 10
            questions_per_user = 5
            
            test_questions = [
                "Bonjour",
                "Qu'est-ce que le cancer du sein ?",
                "Comment faire l'auto-examen ?", 
                "Quels sont les facteurs de risque ?",
                "Merci pour les informations"
            ]
            
            for user_index in range(user_count):
                user_id = f"perf_user_{user_index}"
                for question in test_questions[:questions_per_user]:
                    self.service.process_question(question, user_id)
            
            end_time = time.time()
            total_time = end_time - start_time
            total_operations = user_count * questions_per_user
            
            performance = total_operations / total_time if total_time > 0 else 0
            
            self.logger.print_info(f"Temps total: {total_time:.2f}s")
            self.logger.print_info(f"Opérations: {total_operations}")
            self.logger.print_info(f"Performance: {performance:.2f} opérations/seconde")
            
            if performance >= 1.0:  # Au moins 1 opération par seconde
                self.logger.print_success("Performance acceptable")
            else:
                self.logger.print_warning("Performance faible")
                details.append(f"Performance: {performance:.2f} ops/sec")
            
            # Test 5.2: Utilisation mémoire
            self.logger.print_step("Test 5.2 - Utilisation mémoire")
            
            active_conversations = len(self.service.conversation_manager.conversations)
            total_messages = sum(
                len(history) for history in self.service.conversation_manager.conversations.values()
            )
            
            self.logger.print_info(f"Conversations actives: {active_conversations}")
            self.logger.print_info(f"Messages totaux: {total_messages}")
            
            if active_conversations == user_count:
                self.logger.print_success("Gestion mémoire correcte")
            else:
                self.logger.print_error("Problème de gestion mémoire")
                success = False
                details.append("Gestion mémoire échouée")
            
            self.logger.print_result("Performance et évolutivité", success, "; ".join(details) if details else None)
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            success = False
            self.logger.print_result("Performance et évolutivité", False, f"Erreur: {e}")
        
        return success
    
    def test_error_handling_and_resilience(self):
        """Test la gestion des erreurs et la résilience du système"""
        self.logger.print_separator("🧪 TEST 6: GESTION DES ERREURS ET RÉSILIENCE")
        
        success = True
        details = []
        
        try:
            # Test 6.1: Cas limites et entrées invalides
            self.logger.print_step("Test 6.1 - Cas limites")
            
            edge_cases = [
                ("", "Question vide"),
                ("   ", "Espaces seulement"),
                ("a", "Très court"),
                ("x" * 1000, "Très long"),
                ("¿¿¿???", "Caractères spéciaux"),
                ("123456789", "Chiffres seulement"),
            ]
            
            user_id = f"resilience_{uuid.uuid4().hex[:8]}"
            handled_correctly = 0
            
            for question, description in edge_cases:
                try:
                    response = self.service.process_question(question, user_id)
                    if response and response.get('answer'):
                        handled_correctly += 1
                        self.logger.print_success(f"'{description}' → Géré")
                    else:
                        self.logger.print_warning(f"'{description}' → Réponse vide")
                except Exception as e:
                    self.logger.print_error(f"'{description}' → Erreur: {e}")
            
            resilience_rate = handled_correctly / len(edge_cases) * 100
            
            if resilience_rate >= 80:
                self.logger.print_success(f"Résilience: {resilience_rate:.1f}%")
            else:
                self.logger.print_warning(f"Résilience: {resilience_rate:.1f}%")
                details.append(f"Résilience: {resilience_rate:.1f}%")
            
            # Test 6.2: Récupération après erreur
            self.logger.print_step("Test 6.2 - Récupération après erreur")
            
            # Tester une conversation normale après les cas limites
            normal_question = "Pouvez-vous me parler de la prévention du cancer du sein ?"
            normal_response = self.service.process_question(normal_question, user_id)
            
            if normal_response and normal_response.get('answer'):
                self.logger.print_success("Récupération après erreur réussie")
            else:
                self.logger.print_error("Échec de récupération après erreur")
                success = False
                details.append("Récupération échouée")
            
            self.logger.print_result("Gestion des erreurs et résilience", success, "; ".join(details) if details else None)
            
        except Exception as e:
            self.logger.print_error(f"Erreur pendant le test: {e}")
            success = False
            self.logger.print_result("Gestion des erreurs et résilience", False, f"Erreur: {e}")
        
        return success
    
    def run_all_tests(self):
        """Exécute tous les tests et retourne un résumé"""
        if not self.setup_completed:
            self.logger.print_error("Setup non effectué. Appelez setup() d'abord.")
            return False
        
        self.logger.print_separator("🎯 DÉMARRAGE DE LA SUITE DE TESTS COMPLÈTE", 80)
        
        tests = [
            ("Flux de conversation basique", self.test_basic_conversation_flow),
            ("Détection des questions de suivi", self.test_followup_detection_accuracy),
            ("Gestion de l'historique", self.test_history_management),
            ("Compréhension contextuelle", self.test_contextual_understanding),
            ("Performance et évolutivité", self.test_performance_and_scalability),
            ("Gestion des erreurs et résilience", self.test_error_handling_and_resilience),
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
            except Exception as e:
                self.logger.print_error(f"Test '{test_name}' a échoué avec exception: {e}")
                results.append((test_name, False))
        
        # Affichage du résumé
        self.logger.print_separator("📊 RAPPORT FINAL DES TESTS", 80)
        
        for test_name, result in results:
            status = "✅ RÉUSSI" if result else "❌ ÉCHEC"
            print(f"  {status}: {test_name}")
        
        summary = self.logger.get_summary()
        
        print(f"\n📈 STATISTIQUES:")
        print(f"  Total des tests: {summary['total_tests']}")
        print(f"  Tests réussis: {summary['passed']}")
        print(f"  Tests échoués: {summary['failed']}")
        print(f"  Taux de réussite: {summary['success_rate']:.1f}%")
        print(f"  Durée totale: {summary['duration']}")
        
        # Recommandations
        self.logger.print_separator("💡 RECOMMANDATIONS", 80)
        
        if summary['success_rate'] == 100:
            print("🎉 EXCELLENT! Le système est prêt pour la production.")
            print("   Tous les tests ont été réussis avec succès.")
        elif summary['success_rate'] >= 80:
            print("⚠️  BON! Le système est fonctionnel mais peut être amélioré.")
            print("   Quelques ajustements mineurs sont recommandés.")
        elif summary['success_rate'] >= 60:
            print("🔧 SATISFAISANT! Le système fonctionne mais nécessite des améliorations.")
            print("   Certains aspects critiques doivent être revus.")
        else:
            print("🚨 ATTENTION! Le système présente des problèmes importants.")
            print("   Une révision complète est nécessaire avant le déploiement.")
        
        return summary['success_rate'] >= 80


def main():
    """Point d'entrée principal du script de test"""
    
    tester = ComprehensiveContextMemoryTest()
    
    try:
        # Initialisation
        tester.setup()
        
        # Exécution des tests
        overall_success = tester.run_all_tests()
        
        # Code de sortie
        sys.exit(0 if overall_success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Tests interrompus par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 ERREUR CRITIQUE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()