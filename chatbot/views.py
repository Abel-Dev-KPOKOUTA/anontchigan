
from django.shortcuts import render, redirect

def chatbot_redirect(request):
    return redirect('https://anontchigan-api.streamlit.app/')