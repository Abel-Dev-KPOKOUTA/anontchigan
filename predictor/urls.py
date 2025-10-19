from django.urls import path
from . import views

app_name='predictor'

urlpatterns = [
    path('', views.prediction_page, name='predict'),
    path('image/', views.predict_image, name='predict_image'),
    path('data/', views.predict_data, name='predict_data'),
]