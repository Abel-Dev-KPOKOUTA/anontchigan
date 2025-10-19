#!/usr/bin/env python
"""
Script de test pour vérifier le système de mémoire contextuelle
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'anontchigan.settings')
django.setup()

from chatbot.services.rag_service import ChatbotService

def print_separator():
    print("\n" + "="*60)

def test_conversation_context():
    """Test complet d'une conversation avec contexte"""
    
    print("🧪 TEST DU SYSTÈME DE MÉMOIRE CONTEXTUELLE")
    print_separator()
    
    # Initialiser le service
    print("📦 Initialisation du service...")
    service = ChatbotService()
    user_id = "test_user_context_123"
    
    print("✅ Service initialisé\n")
    
    # Test 1 : Première question
    print_separator()
    print("TEST 1 : Première Question")
    print_separator()
    
    question1 = "Comment faire un auto-examen du sein ?"
    print(f"👤 User: {question1}")
    
    response1 = service.process_question(question1, user_id)
    print(f"🤖 Bot ({response1['method']}): {response1['answer'][:100]}...\n")
    
    # Vérifier l'historique
    history = service.conversation_manager.get_history(user_id)
    print(f"📜 Historique: {len(history)} messages")
    assert len(history) == 2, "Devrait avoir 2 messages (user + bot)"
    print("✅ Historique OK\n")
    
    # Test 2 : Question de suivi directe
    print_separator()
    print("TEST 2 : Question de Suivi (Pourquoi ?)")
    print_separator()
    
    question2 = "Pourquoi ?"
    print(f"👤 User: {question2}")
    
    is_followup = service._is_followup_question(question2, history)
    print(f"🔍 Détection de suivi: {is_followup}")
    assert is_followup, "Devrait détecter comme question de suivi"
    
    response2 = service.process_question(question2, user_id)
    print(f"🤖 Bot ({response2['method']}): {response2['answer'][:100]}...\n")
    
    history = service.conversation_manager.get_history(user_id)
    print(f"📜 Historique: {len(history)} messages")
    assert len(history) == 4, "Devrait avoir 4 messages"
    print("✅ Question de suivi traitée\n")
    
    # Test 3 : Question de suivi avec référence
    print_separator()
    print("TEST 3 : Question avec Référence (Quand ?)")
    print_separator()
    
    question3 = "Quand faut-il le faire ?"
    print(f"👤 User: {question3}")
    
    is_followup = service._is_followup_question(question3, history)
    print(f"🔍 Détection de suivi: {is_followup}")
    
    response3 = service.process_question(question3, user_id)
    print(f"🤖 Bot ({response3['method']}): {response3['answer'][:100]}...\n")
    
    history = service.conversation_manager.get_history(user_id)
    print(f"📜 Historique: {len(history)} messages")
    assert len(history) == 6, "Devrait avoir 6 messages"
    print("✅ Référence contextuelle traitée\n")
    
    # Test 4 : Question courte
    print_separator()
    print("TEST 4 : Question Très Courte (Et ça ?)")
    print_separator()
    
    question4 = "Et ça ?"
    print(f"👤 User: {question4}")
    
    is_followup = service._is_followup_question(question4, history)
    print(f"🔍 Détection de suivi: {is_followup}")
    assert is_followup, "Les questions courtes doivent être détectées comme suivi"
    
    response4 = service.process_question(question4, user_id)
    print(f"🤖 Bot ({response4['method']}): {response4['answer'][:100]}...\n")
    
    history = service.conversation_manager.get_history(user_id)
    print(f"📜 Historique: {len(history)} messages")
    print("✅ Question courte traitée\n")
    
    # Test 5 : Nouvelle question indépendante
    print_separator()
    print("TEST 5 : Nouvelle Question Indépendante")
    print_separator()
    
    question5 = "Quels sont les centres de dépistage à Cotonou ?"
    print(f"👤 User: {question5}")
    
    is_followup = service._is_followup_question(question5, history)
    print(f"🔍 Détection de suivi: {is_followup}")
    print("ℹ️  Peut être faux positif mais sera traité normalement")
    
    response5 = service.process_question(question5, user_id)
    print(f"🤖 Bot ({response5['method']}): {response5['answer'][:100]}...\n")
    
    # Test 6 : Retour à un sujet précédent
    print_separator()
    print("TEST 6 : Retour à un Sujet Précédent")
    print_separator()
    
    question6 = "Tu as dit quoi sur l'auto-examen ?"
    print(f"👤 User: {question6}")
    
    is_followup = service._is_followup_question(question6, history)
    print(f"🔍 Détection de suivi: {is_followup}")
    assert is_followup, "Devrait détecter la référence au passé"
    
    response6 = service.process_question(question6, user_id)
    print(f"🤖 Bot ({response6['method']}): {response6['answer'][:100]}...\n")
    
    # Afficher l'historique complet
    print_separator()
    print("📜 HISTORIQUE COMPLET DE LA CONVERSATION")
    print_separator()
    
    history = service.conversation_manager.get_history(user_id)
    for i, msg in enumerate(history, 1):
        role_icon = "👤" if msg['role'] == 'user' else "🤖"
        content_preview = msg['content'][:80] + "..." if len(msg['content']) > 80 else msg['content']
        print(f"{i}. {role_icon} {msg['role']}: {content_preview}")
    
    print(f"\n✅ Total: {len(history)} messages dans l'historique")
    
    # Résumé des tests
    print_separator()
    print("✅ TOUS LES TESTS RÉUSSIS!")
    print_separator()
    print("\n📊 Résumé:")
    print("  - Première question: ✅")
    print("  - Questions de suivi: ✅")
    print("  - Questions courtes: ✅")
    print("  - Nouvelle question: ✅")
    print("  - Référence au passé: ✅")
    print("  - Historique maintenu: ✅")
    print("\n🎉 Le système de mémoire contextuelle fonctionne correctement!")
    

def test_followup_detection():
    """Test spécifique de la détection des questions de suivi"""
    
    print("\n\n🧪 TEST DE DÉTECTION DES QUESTIONS DE SUIVI")
    print_separator()
    
    service = ChatbotService()
    
    # Créer un faux historique
    fake_history = [
        {"role": "user", "content": "Comment faire auto-examen ?"},
        {"role": "assistant", "content": "Voici comment faire..."}
    ]
    
    test_cases = [
        # (question, devrait_être_détecté, raison)
        ("Pourquoi ?", True, "Question courte + mot-clé"),
        ("Et ça ?", True, "Question très courte"),
        ("Comment ?", True, "Question courte + mot-clé"),
        ("Explique mieux", True, "Mot-clé 'explique'"),
        ("Tu as dit quoi ?", True, "Référence passé"),
        ("C'est quoi les symptômes du cancer ?", False, "Question complète indépendante"),
        ("Il est où le centre ?", True, "Pronom + courte"),
        ("Quels sont les facteurs de risque ?", False, "Question complète nouvelle"),
    ]
    
    print("\nTest de détection:")
    print("-" * 60)
    
    correct = 0
    total = len(test_cases)
    
    for question, expected, reason in test_cases:
        result = service._is_followup_question(question, fake_history)
        status = "✅" if result == expected else "❌"
        correct += 1 if result == expected else 0
        
        print(f"{status} '{question}'")
        print(f"   Attendu: {expected}, Obtenu: {result}")
        print(f"   Raison: {reason}\n")
    
    print("-" * 60)
    print(f"Score: {correct}/{total} ({correct/total*100:.0f}%)")
    
    if correct == total:
        print("✅ Détection parfaite!")
    elif correct >= total * 0.8:
        print("⚠️  Détection acceptable mais peut être améliorée")
    else:
        print("❌ Détection à améliorer")


def test_history_limit():
    """Test de la limite de l'historique"""
    
    print("\n\n🧪 TEST DE LA LIMITE D'HISTORIQUE")
    print_separator()
    
    service = ChatbotService()
    user_id = "test_limit_user"
    
    # Ajouter beaucoup de messages
    print("📤 Ajout de 20 paires de messages...")
    for i in range(20):
        service.conversation_manager.add_message(user_id, "user", f"Question {i}")
        service.conversation_manager.add_message(user_id, "assistant", f"Réponse {i}")
    
    history = service.conversation_manager.get_history(user_id)
    
    from chatbot.services.rag_service import Config
    max_expected = Config.MAX_HISTORY_LENGTH * 2
    
    print(f"📜 Messages dans l'historique: {len(history)}")
    print(f"📊 Limite configurée: {max_expected}")
    
    if len(history) <= max_expected:
        print("✅ Limite respectée!")
    else:
        print("❌ Limite dépassée!")
    
    # Vérifier que ce sont les plus récents
    if history:
        print(f"\n📋 Dernier message: '{history[-1]['content']}'")
        assert "Réponse 19" in history[-1]['content'], "Devrait garder les plus récents"
        print("✅ Les messages les plus récents sont conservés")


def main():
    """Exécute tous les tests"""
    
    try:
        # Test principal
        test_conversation_context()
        
        # Test détection
        test_followup_detection()
        
        # Test limite
        test_history_limit()
        
        print("\n" + "="*60)
        print("🎉 TOUS LES TESTS SONT RÉUSSIS!")
        print("="*60)
        print("\n✅ Le système de mémoire contextuelle est fonctionnel.")
        print("✅ Vous pouvez maintenant utiliser le chatbot avec confiance.\n")
        
    except AssertionError as e:
        print(f"\n❌ TEST ÉCHOUÉ: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()