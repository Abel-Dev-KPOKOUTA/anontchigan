import requests
import json
import time

def test_chatbot():
    """Test complet du chatbot ANONTCHIGAN"""
    base_url = "http://127.0.0.1:8000/chatbot/ask/"
    
    print("🚀 DÉMARRAGE DES TESTS DU CHATBOT ANONTCHIGAN")
    print("=" * 60)
    
    # Liste des questions de test
    test_questions = [
        # Salutations
        "cc",
        "bonjour",
        "salut",
        "hello",
        
        # Questions identité
        "qui es-tu ?",
        "qui est anontchigan ?",
        "que signifie ton nom ?",
        "qui t'a créé ?",
        "c'est quoi le club IA de l'ENSGMM ?",
        
        # Questions directes (doivent trouver des réponses en JSON)
        "Qu'est-ce que le cancer du sein ?",
        "Quels sont les symptômes du cancer du sein ?", 
        "Comment faire l'auto-examen des seins ?",
        "Quels sont les facteurs de risque ?",
        "C'est quoi une mammographie ?",
        
        # Questions pour la génération Groq
        "Quels sont les derniers traitements innovants ?",
        "Comment soutenir une personne atteinte du cancer du sein ?",
        "Quelle est l'importance du dépistage précoce ?",
        "Peux-tu me conseiller sur l'alimentation pour prévenir le cancer ?",
        
        # Questions hors sujet (pour tester la gestion d'erreur)
        "Quel temps fait-il aujourd'hui ?",
        "Qui a gagné le match de football ?",
        "Comment cuisiner le riz ?"
    ]
    
    results = {
        "success": 0,
        "errors": 0,
        "response_times": []
    }
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n{'='*60}")
        print(f"🧪 TEST {i}/{len(test_questions)}")
        print(f"❓ Question: {question}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                base_url,
                json={"question": question},
                headers={"Content-Type": "application/json"},
                timeout=30  # 30 secondes max
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            results["response_times"].append(response_time)
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"✅ RÉUSSITE")
                print(f"📝 Réponse: {data['answer'][:100]}..." if len(data['answer']) > 100 else f"📝 Réponse: {data['answer']}")
                print(f"🔧 Méthode: {data['source']}")
                print(f"🎯 Score: {data.get('score', 'N/A')}")
                print(f"⏱️  Temps: {response_time:.2f}s")
                print(f"⏰ Horodatage: {data['timestamp']}")
                
                # Vérifications de qualité
                check_response_quality(data['answer'])
                
                results["success"] += 1
                
            else:
                print(f"❌ ERREUR HTTP: {response.status_code}")
                print(f"📄 Détails: {response.text}")
                results["errors"] += 1
                
        except requests.exceptions.Timeout:
            print(f"⏰ TIMEOUT: La requête a pris trop de temps")
            results["errors"] += 1
        except requests.exceptions.ConnectionError:
            print(f"🔌 ERREUR CONNEXION: Impossible de se connecter au serveur")
            results["errors"] += 1
        except Exception as e:
            print(f"💥 EXCEPTION: {e}")
            results["errors"] += 1
    
    # Résumé final
    print(f"\n{'='*60}")
    print("📊 RÉSUMÉ DES TESTS")
    print(f"✅ Tests réussis: {results['success']}")
    print(f"❌ Tests en échec: {results['errors']}")
    print(f"📈 Taux de succès: {(results['success']/len(test_questions))*100:.1f}%")
    
    if results["response_times"]:
        avg_time = sum(results["response_times"]) / len(results["response_times"])
        print(f"⏱️  Temps moyen de réponse: {avg_time:.2f}s")
        print(f"⚡ Temps le plus rapide: {min(results['response_times']):.2f}s")
        print(f"🐌 Temps le plus lent: {max(results['response_times']):.2f}s")
    
    print("🎯 Tests terminés !")

def check_response_quality(answer):
    """Vérifie la qualité de la réponse"""
    checks = {
        "Réponse non vide": len(answer.strip()) > 0,
        "Longueur minimale": len(answer) >= 30,
        "Réponse complète": not answer.endswith(('...', ',', ';')),
        "Emojis présents": any(emoji in answer for emoji in ['💗', '🌸', '😊', '🇧🇯']),
        "Point final": answer.strip().endswith(('.', '!', '?')),
    }
    
    print("🔍 Vérification qualité:")
    for check_name, check_result in checks.items():
        status = "✅" if check_result else "❌"
        print(f"   {status} {check_name}")

def test_performance():
    """Test de performance avec des requêtes répétées"""
    print(f"\n{'='*60}")
    print("⚡ TEST DE PERFORMANCE")
    
    base_url = "http://127.0.0.1:8000/chatbot/ask/"
    test_question = "Qu'est-ce que le cancer du sein ?"
    
    times = []
    
    for i in range(5):  # 5 requêtes successives
        try:
            start_time = time.time()
            
            response = requests.post(
                base_url,
                json={"question": test_question},
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            times.append(response_time)
            
            print(f"   Requête {i+1}: {response_time:.2f}s - Status: {response.status_code}")
            
        except Exception as e:
            print(f"   Requête {i+1}: Erreur - {e}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"   📊 Moyenne: {avg_time:.2f}s")
        print(f"   📈 Écart: {max(times)-min(times):.2f}s")

if __name__ == "__main__":
    # Vérifier que le serveur est démarré
    print("🔍 Vérification du serveur...")
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=5)
        print("✅ Serveur Django détecté")
    except:
        print("❌ Serveur non détecté! Assurez-vous que 'python manage.py runserver' est lancé")
        exit(1)
    
    # Lancer les tests principaux
    test_chatbot()
    
    # Lancer le test de performance
    test_performance()
    
    print(f"\n🎉 Tous les tests sont terminés !")
    print("💡 Conseils:")
    print("   - Vérifiez les logs Django pour plus de détails")
    print("   - Testez aussi via l'interface web: http://127.0.0.1:8000/chatbot/")
    print("   - Consultez le fichier anontchigan.log pour les logs détaillés")