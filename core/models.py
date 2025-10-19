from django.db import models
from django.utils import timezone

class ContactMessage(models.Model):
    """
    Modèle pour stocker les messages de contact
    """
    SUJET_CHOICES = [
        ('question', 'Question générale'),
        ('support', 'Support technique'),
        ('depistage', 'Demande de dépistage'),
        ('partenariat', 'Partenariat'),
        ('autre', 'Autre'),
    ]
    
    nom = models.CharField(max_length=200, verbose_name="Nom complet")
    email = models.EmailField(verbose_name="Email")
    telephone = models.CharField(max_length=20, blank=True, verbose_name="Téléphone")
    sujet = models.CharField(max_length=50, choices=SUJET_CHOICES, verbose_name="Sujet")
    message = models.TextField(verbose_name="Message")
    date_envoi = models.DateTimeField(default=timezone.now, verbose_name="Date d'envoi")
    traite = models.BooleanField(default=False, verbose_name="Traité")
    
    class Meta:
        verbose_name = "Message de contact"
        verbose_name_plural = "Messages de contact"
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"{self.nom} - {self.get_sujet_display()} ({self.date_envoi.strftime('%d/%m/%Y')})"


class Newsletter(models.Model):
    """
    Modèle pour les inscriptions à la newsletter
    """
    email = models.EmailField(unique=True, verbose_name="Email")
    nom = models.CharField(max_length=200, blank=True, verbose_name="Nom")
    date_inscription = models.DateTimeField(default=timezone.now, verbose_name="Date d'inscription")
    actif = models.BooleanField(default=True, verbose_name="Actif")
    
    class Meta:
        verbose_name = "Abonné newsletter"
        verbose_name_plural = "Abonnés newsletter"
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.email} ({self.date_inscription.strftime('%d/%m/%Y')})"