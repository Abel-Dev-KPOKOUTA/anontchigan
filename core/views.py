from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib import messages

# Page d'accueil
def accueil(request):
    """
    Vue pour la page d'accueil
    """
    context = {
        'page_title': 'Accueil',
    }
    return render(request, 'core/accueil.html', context)

# Page à propos
def a_propos(request):
    """
    Vue pour la page À Propos
    """
    context = {
        'page_title': 'À Propos',
    }
    return render(request, 'core/a_propos.html', context)

# Page contact
def contact(request):
    """
    Vue pour la page Contact avec gestion du formulaire
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone', '')
        sujet = request.POST.get('sujet')
        message_text = request.POST.get('message')
        
        # Validation basique
        if nom and email and sujet and message_text:
            # TODO: Envoyer l'email ou sauvegarder en base de données
            # Pour l'instant, on affiche juste un message de succès
            
            # Exemple: Sauvegarde dans un modèle (à créer)
            # ContactMessage.objects.create(
            #     nom=nom,
            #     email=email,
            #     telephone=telephone,
            #     sujet=sujet,
            #     message=message_text
            # )
            
            messages.success(
                request, 
                f'Merci {nom} ! Votre message a été envoyé avec succès. Nous vous répondrons dans les plus brefs délais.'
            )
        else:
            messages.error(
                request, 
                'Veuillez remplir tous les champs obligatoires.'
            )
    
    context = {
        'page_title': 'Contact',
    }
    return render(request, 'core/contact.html', context)


def politique(request):
    return render(request,'core/politique.html')