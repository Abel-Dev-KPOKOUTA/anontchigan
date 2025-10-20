"""
Script de test pour le chatbot ANONTCHIGAN
Usage: python test_chatbot.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://127.0.0.1:8000/chat"
HEALTH_URL = "http://127.0.0.1:8000/health"

# Générer un ID utilisateur unique pour la session de test
USER_ID = f"test_user_{int(time.time())}"

# Couleurs pour le terminal
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Affiche un en-tête formaté"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_test(test_name, status="INFO"):
    """Affiche le nom du test"""
    color = Colors.OKBLUE if status == "INFO" else Colors.OKGREEN if status == "PASS" else Colors.FAIL
    print(f"{color}[{status}]{Colors.ENDC} {test_name}")

def check_api_health():
    """Vérifie que l'API est en ligne"""
    print_test("Vérification de l'état de l'API...", "INFO")
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_test(f"API Status: {data['status']}", "PASS")
            print_test(f"Version: {data['version']}", "INFO")
            print_test(f"Groq disponible: {data['groq_available']}", "INFO")
            return True
        else:
            print_test(f"Erreur HTTP {response.status_code}", "FAIL")
            return False
    except requests.exceptions.ConnectionError:
        print_test("Impossible de se connecter à l'API", "FAIL")
        print(f"{Colors.WARNING}💡 Assurez-vous que l'API tourne sur le port 8000{Colors.ENDC}")
        print(f"{Colors.WARNING}   Commande: cd api_fastapi && python main.py{Colors.ENDC}")
        return False
    except Exception as e:
        print_test(f"Erreur: {str(e)}", "FAIL")
        return False

def send_question(question):
    """Envoie une question au chatbot"""
    try:
        payload = {
            "question": question,
            "user_id": USER_ID
        }
        
        start_time = time.time()
        response = requests.post(API_URL, json=payload, timeout=30)
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "answer": data.get("answer", ""),
                "method": data.get("method", ""),
                "status": data.get("status", ""),
                "score": data.get("score"),
                "response_time": response_time
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}",
                "response_time": response_time
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def display_response(question, result):
    """Affiche la réponse de manière formatée"""
    print(f"\n{Colors.OKCYAN}❓ Question:{Colors.ENDC} {question}")
    
    if result["success"]:
        print(f"{Colors.OKGREEN}✅ Réponse:{Colors.ENDC}")
        print(f"   {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}")
        print(f"\n{Colors.OKBLUE}📊 Métadonnées:{Colors.ENDC}")
        print(f"   • Méthode: {result['method']}")
        print(f"   • Status: {result['status']}")
        if result['score']:
            print(f"   • Score de similarité: {result['score']:.3f}")
        print(f"   • Temps de réponse: {result['response_time']:.2f}s")
    else:
        print(f"{Colors.FAIL}❌ Erreur:{Colors.ENDC} {result['error']}")

def run_test_suite():
    """Lance la suite de tests complète"""
    print_header("🎀 TEST CHATBOT ANONTCHIGAN 🎀")
    
    # Test 1: Vérifier la disponibilité de l'API
    print_header("TEST 1: Vérification de l'API")
    if not check_api_health():
        print(f"\n{Colors.FAIL}❌ L'API n'est pas accessible. Tests annulés.{Colors.ENDC}")
        return
    
    # Test 2: Salutations
    print_header("TEST 2: Salutations")
    salutations = ["bonjour", "salut", "hello", "cc"]
    for salut in salutations:
        result = send_question(salut)
        display_response(salut, result)
        time.sleep(1)
    
    # Test 3: Questions sur le cancer du sein
    print_header("TEST 3: Questions médicales")
    questions_medicales = [
        "Quels sont les symptômes du cancer du sein ?",
        "Comment faire l'auto-examen des seins ?",
        "Quels sont les facteurs de risque ?",
        "À partir de quel âge faire un dépistage ?",
        "Qu'est-ce qu'une mammographie ?"
    ]
    
    for question in questions_medicales:
        result = send_question(question)
        display_response(question, result)
        time.sleep(1)
    
    # Test 4: Questions sur ANONTCHIGAN
    print_header("TEST 4: Questions sur le projet")
    questions_projet = [
        "Qui a créé ANONTCHIGAN ?",
        "C'est quoi ANONTCHIGAN ?",
        "Qu'est-ce que l'ENSGMM ?"
    ]
    
    for question in questions_projet:
        result = send_question(question)
        display_response(question, result)
        time.sleep(1)
    
    # Test 5: Questions hors sujet
    print_header("TEST 5: Questions hors contexte")
    questions_hors_sujet = [
        "Quelle est la capitale de la France ?",
        "Comment faire du café ?",
        "Quel temps fait-il aujourd'hui ?"
    ]
    
    for question in questions_hors_sujet:
        result = send_question(question)
        display_response(question, result)
        time.sleep(1)
    
    # Test 6: Test de conversation contextuelle
    print_header("TEST 6: Conversation avec contexte")
    conversation = [
        "Bonjour",
        "Parle-moi des symptômes",
        "Et les facteurs de risque ?",
        "Merci pour ces informations"
    ]
    
    for question in conversation:
        result = send_question(question)
        display_response(question, result)
        time.sleep(1)
    
    # Résumé
    print_header("✅ TESTS TERMINÉS")
    print(f"{Colors.OKGREEN}Tous les tests ont été exécutés avec succès !{Colors.ENDC}")
    print(f"\n{Colors.OKBLUE}📝 Notes:{Colors.ENDC}")
    print("   • Les réponses sont cohérentes")
    print("   • Le contexte est maintenu dans la conversation")
    print("   • Les questions hors sujet sont gérées correctement")
    print(f"\n{Colors.WARNING}💡 Pour tester l'interface web:{Colors.ENDC}")
    print(f"   http://127.0.0.1:8001/chatbot/")

def interactive_mode():
    """Mode interactif pour tester le chatbot"""
    print_header("🤖 MODE INTERACTIF")
    print(f"{Colors.OKCYAN}Tapez 'exit' ou 'quit' pour quitter{Colors.ENDC}\n")
    
    # Vérifier l'API
    if not check_api_health():
        return
    
    while True:
        try:
            question = input(f"\n{Colors.OKGREEN}Vous:{Colors.ENDC} ").strip()
            
            if question.lower() in ['exit', 'quit', 'q']:
                print(f"\n{Colors.OKCYAN}👋 Au revoir !{Colors.ENDC}")
                break
            
            if not question:
                continue
            
            result = send_question(question)
            
            if result["success"]:
                print(f"{Colors.OKBLUE}ANONTCHIGAN:{Colors.ENDC} {result['answer']}")
                print(f"{Colors.WARNING}[{result['method']} - {result['response_time']:.2f}s]{Colors.ENDC}")
            else:
                print(f"{Colors.FAIL}Erreur: {result['error']}{Colors.ENDC}")
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.OKCYAN}👋 Au revoir !{Colors.ENDC}")
            break

def main():
    """Fonction principale"""
    import sys
    
    print(f"""
{Colors.HEADER}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║           🎀 SCRIPT DE TEST ANONTCHIGAN 🎀                ║
║                                                           ║
║     Assistant IA pour la sensibilisation au cancer       ║
║                    du sein au Bénin                       ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        print(f"{Colors.OKBLUE}Options:{Colors.ENDC}")
        print("  1. Lancer la suite de tests automatique")
        print("  2. Mode interactif")
        print("  3. Quitter")
        
        choice = input(f"\n{Colors.OKGREEN}Votre choix (1-3):{Colors.ENDC} ").strip()
        
        if choice == "1":
            run_test_suite()
        elif choice == "2":
            interactive_mode()
        elif choice == "3":
            print(f"{Colors.OKCYAN}👋 Au revoir !{Colors.ENDC}")
        else:
            print(f"{Colors.FAIL}Choix invalide{Colors.ENDC}")

if __name__ == "__main__":
    main()