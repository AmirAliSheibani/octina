from django.urls import path
from . import views

app_name = 'price'

urlpatterns = [
    path('procces/<str:pk>/', views.process_pricing, name='procces_pricing')
]