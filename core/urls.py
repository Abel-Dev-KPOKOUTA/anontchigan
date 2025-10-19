from django.urls import path, include
from .import views

#app_name='core'

urlpatterns = [
    # Routes avec fonctions de vues
    path('', views.accueil, name='accueil'),
    path('a-propos/', views.a_propos, name='a_propos'),
    path('contact/', views.contact, name='contact'),
    path('politique-confidentialite/', views.politique, name='politique'),
    
]