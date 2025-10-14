from django.urls import path
from .import views

app_name='chatbot'

urlpatterns = [
    path('' ,views.chatbot_page, name='chat'),
    path('ask/', views.chatbot_ask, name='chat_ask'),
]
