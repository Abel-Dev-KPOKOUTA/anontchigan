# 🎀 ANONTCHIGAN

![Octobre Rose 2025](https://img.shields.io/badge/Octobre%20Rose-2025-FF69B4?style=for-the-badge)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=for-the-badge&logo=django)
![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-Proprietary-red?style=for-the-badge)

**Intelligence Artificielle pour la Sensibilisation au Cancer du Sein**

---

## 📖 À Propos

**ANONTCHIGAN** est une plateforme web d'intelligence artificielle développée pour sensibiliser et éduquer sur le cancer du sein. Le projet combine :

- 🤖 **Un chatbot éducatif** qui répond aux questions sur la prévention, les symptômes et l'auto-examen
- 🧠 **Un outil d'analyse d'images radiographiques** capable d'indiquer si une tumeur semble bénigne ou maligne

> ⚠️ **Important** : ANONTCHIGAN ne remplace pas un médecin. Les réponses et prédictions sont informatives et éducatives uniquement, non diagnostiques.

---

## 👥 Équipe de Développement

Ce projet a été développé par des étudiants du **Club IA de l'ENSGMM** (École Nationale Supérieure de Génie Mathématique et Modélisation) d'Abomey :

- **Judicaël Karol DOBOEVI**
- **Hornel Ursus GBAGUIDI**
- **Abel Kocou KPOKOUTA**
- **Josaphat ADJELE**

---

## 🎯 Objectifs du Projet

1. **Sensibiliser** la population sur le cancer du sein
2. **Éduquer** sur l'importance du dépistage précoce
3. **Faciliter** l'accès à l'information médicale fiable
4. **Démocratiser** l'utilisation de l'IA dans la santé préventive

---

## 🚀 Fonctionnalités

### ✅ Actuellement Disponibles

- ✨ **Interface web responsive** et accessible
- 📱 Design adapté mobile/tablette/desktop
- 📄 Pages d'information complètes
- 📧 Formulaire de contact fonctionnel
- 🔒 Politique de confidentialité détaillée

### 🚧 En Développement

- 🤖 **Chatbot RAG** (Retrieval-Augmented Generation)
  - Base de connaissances FAQ validée
  - Recherche sémantique avec embeddings
  - Réponses contextualisées sans hallucinations
  
- 🧠 **Modèle de Prédiction IA**
  - Analyse de données tabulaires (symptômes)
  - Traitement d'images radiographiques
  - Estimation bénin/malin avec probabilités

---

## 🛠️ Technologies Utilisées

### Backend
- **Django 4.2+** - Framework web Python
- **Python 3.8+** - Langage de programmation
- **SQLite** - Base de données (dev)

### Intelligence Artificielle (à venir)
- **Sentence Transformers** - Embeddings textuels
- **FAISS** - Recherche vectorielle
- **TensorFlow/Keras** - Analyse d'images
- **Scikit-learn** - Machine Learning

### Frontend
- **HTML5** - Structure
- **CSS3** - Design responsive
- **JavaScript** - Interactivité
- **Font Awesome** - Icônes

---

## 📦 Installation

### Prérequis
```bash
Python 3.8+
pip
virtualenv
```

### Installation Rapide

```bash
# Cloner le projet
git clone https://github.com/votre-repo/anontchigan.git
cd anontchigan

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Installer les dépendances
pip install -r requirements.txt

# Effectuer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Visitez : http://127.0.0.1:8000/

📖 Pour plus de détails, consultez [INSTALLATION.md](INSTALLATION.md)

---

## 📂 Structure du Projet

```
anontchigan/
├── manage.py
├── anontchigan/           # Configuration Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── core/                  # App principale
│   ├── templates/
│   │   └── core/
│   │       ├── base.html
│   │       ├── accueil.html
│   │       ├── a_propos.html
│   │       ├── contact.html
│   │       └── politique.html
│   ├── views.py
│   ├── urls.py
│   ├── models.py
│   └── admin.py
├── chatbot/               # À développer
└── predictor/             # À développer
```

---

## 🎨 Pages Disponibles

| Page | URL | Description |
|------|-----|-------------|
| 🏠 Accueil | `/` | Page principale avec services |
| ℹ️ À Propos | `/a-propos/` | Présentation du projet et de l'équipe |
| 📧 Contact | `/contact/` | Formulaire de contact et centres de dépistage |
| 📜 Politique | `/politique-confidentialite/` | Confidentialité et conditions d'utilisation |
| ⚙️ Admin | `/admin/` | Interface d'administration Django |

---

## 🔒 Confidentialité & Sécurité

- ✅ **Aucune collecte** de données personnelles
- ✅ **Suppression automatique** des images après traitement
- ✅ **Traitement local** des requêtes
- ✅ **Conformité** aux normes de protection des données

Pour plus d'informations : [Politique de Confidentialité](http://127.0.0.1:8000/politique-confidentialite/)

---

## 📝 Licence & Propriété Intellectuelle

**Tous droits réservés © 2025**

Le modèle, le nom **ANONTCHIGAN** et tout le contenu associé sont la propriété exclusive de :
- Judicaël Karol DOBOEVI
- Hornel Ursus GBAGUIDI
- Abel Kocou KPOKOUTA
- Josaphat ADJELE

❌ **Toute reproduction ou diffusion non autorisée est interdite.**

---

## 📞 Contact

📧 **Email** : contact.anontchigan@gmail.com

🏫 **Institution** : ENSGMM - École Nationale Supérieure de Génie Mathématique et Modélisation

📍 **Localisation** : Abomey, Bénin

---

## 🤝 Contribuer

Ce projet est actuellement fermé aux contributions externes. Pour toute suggestion ou partenariat, veuillez nous contacter par email.

---

## 🌟 Remerciements

- **ENSGMM** - Pour le soutien institutionnel
- **Club IA** - Pour l'environnement collaboratif
- **Octobre Rose** - Pour l'inspiration et la cause

---

## ⚠️ Avertissement Médical

**ANONTCHIGAN est un outil éducatif et de sensibilisation.**

Les résultats produits par l'IA peuvent comporter des erreurs. Les concepteurs ne sont pas responsables des décisions médicales prises à partir des réponses de l'IA.

**Consultez toujours un professionnel de santé qualifié pour tout diagnostic ou traitement.**

L'outil est conçu pour l'éducation, la recherche et la prévention uniquement.

---

<div align="center">

**Fait avec ❤️ pour Octobre Rose 2025**

🎀 **Sensibilisons ensemble contre le cancer du sein** 🎀

</div>
