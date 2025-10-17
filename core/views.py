from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage
import logging
from django.utils import timezone
# Configuration du logger
logger = logging.getLogger(__name__)

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
    Vue pour la page Contact avec gestion complète du formulaire
    """
    if request.method == 'POST':
        # Récupération des données du formulaire
        nom = request.POST.get('nom', '').strip()
        email = request.POST.get('email', '').strip()
        telephone = request.POST.get('telephone', '').strip()
        sujet = request.POST.get('sujet', '')
        message_text = request.POST.get('message', '').strip()

        # Validation des données
        erreurs = []

        if not nom:
            erreurs.append("Le nom est obligatoire.")
        elif len(nom) < 2:
            erreurs.append("Le nom doit contenir au moins 2 caractères.")

        if not email:
            erreurs.append("L'email est obligatoire.")
        elif '@' not in email:
            erreurs.append("L'adresse email n'est pas valide.")

        if not sujet:
            erreurs.append("Veuillez sélectionner un sujet.")

        if not message_text:
            erreurs.append("Le message ne peut pas être vide.")
        elif len(message_text) < 10:
            erreurs.append("Le message est trop court (minimum 10 caractères).")

        # Si il y a des erreurs, on les affiche
        if erreurs:
            for erreur in erreurs:
                messages.error(request, erreur)
        else:
            try:
                # ✅ SAUVEGARDE dans la base de données avec le modèle ContactMessage
                contact_message = ContactMessage.objects.create(
                    nom=nom,
                    email=email,
                    telephone=telephone if telephone else '',
                    sujet=sujet,
                    message=message_text
                )


                # ✅ Tentative d'envoi d'email (optionnel - pour développement)
                try:
                    # Email pour l'administrateur
                    sujet_admin = f"ANONTCHIGAN - Nouveau message de {nom}"
                    message_admin = f"""
                    Nouveau message reçu via le formulaire de contact :

                    Nom : {nom}
                    Email : {email}
                    Téléphone : {telephone if telephone else 'Non renseigné'}
                    Sujet : {contact_message.get_sujet_display()}

                    Message :
                    {message_text}

                    ---
                    Message envoyé le : {timezone.localtime(contact_message.date_envoi).strftime('%d/%m/%Y à %H:%M')}
                    """

                    send_mail(
                        sujet_admin,
                        message_admin,
                        settings.DEFAULT_FROM_EMAIL,
                        ['kpokoutaabel@gmail.com','anontchigan@gmail.com','judikardo@gmail.com'], # destinataire
                        fail_silently=True,  # Ne pas planter si l'email échoue
                    )

                    # Email de confirmation à l'utilisateur
                    sujet_confirmation = "ANONTCHIGAN - Confirmation de réception"
                    message_confirmation = f"""
                    Bonjour {nom},

                    Nous avons bien reçu votre message et vous en remercions.

                    Résumé de votre demande :
                    - Sujet : {contact_message.get_sujet_display()}
                    - Date : {timezone.localtime(contact_message.date_envoi).strftime('%d/%m/%Y à %H:%M')}
                    - Référence : #{contact_message.id}

                    Nous traitons votre demande dans les meilleurs délais et vous répondrons dans un délai de 24 à 48 heures.

                    Cordialement,
                    L'équipe ANONTCHIGAN
                    Club IA - ENSGMM Abomey
                    """

                    send_mail(
                        sujet_confirmation,
                        message_confirmation,
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True,
                    )

                except Exception as e:
                    logger.warning(f"Email non envoyé : {e}")
                    # On continue même si l'email échoue

                # ✅ Message de succès
                messages.success(
                    request,
                    f'✅ <strong>Merci {nom} !</strong><br>'
                    f'Votre message a été envoyé avec succès. '
                    f'Nous vous répondrons dans les plus brefs délais.'
                )

                # ✅ Réinitialisation du formulaire
                return redirect('contact')

            except Exception as e:
                logger.error(f"Erreur sauvegarde message: {e}")
                messages.error(
                    request,
                    '❌ Une erreur est survenue lors de l\'envoi de votre message. '
                    'Veuillez réessayer.'
                )

    # Contexte pour le template
    context = {
        'page_title': 'Contact',
    }
    return render(request, 'core/contact.html', context)

def politique(request):
    """
    Vue pour la page Politique de confidentialité
    """
    return render(request, 'core/politique.html')