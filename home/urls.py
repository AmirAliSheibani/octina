from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('service/', views.service, name='service'),
    path('team/', views.team, name='team'),
    path('why/', views.why, name='why'),
    path('mores/<int:pk>', views.slidermore, name='slidermore'),
]
