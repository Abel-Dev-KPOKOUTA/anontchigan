from django.urls import path
from . import views

app_name = 'chatbot'

urlpatterns = [
    path('', views.chatbot_view, name='chat'),
    path('api/chat/', views.chat_api, name='chat_api'),
    path('api/health/', views.health_check, name='health_check'),  # Health check
]