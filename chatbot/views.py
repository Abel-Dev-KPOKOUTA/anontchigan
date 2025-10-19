from django.shortcuts import render

def chatbot_view(request):
    """Affiche simplement l'interface du chatbot"""
    return render(request, 'chatbot/chatbot.html')