from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('slider/readmore/', views.SliderMoreView.as_view(), name='slider_more'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('services/', views.ServiceView.as_view(), name='services'),
    path('team/', views.TeamView.as_view(), name='team'),
    path('why-us/', views.WhyUsView.as_view(), name='why_us'),
]
