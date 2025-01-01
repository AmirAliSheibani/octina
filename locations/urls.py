from django.urls import path
from . import views

app_name = 'locations'

urlpatterns = [
    path('set_location/', views.get_staff_location, name='get_staff_location'),
    path('set_your_location/', views.get_user_location, name='get_user_location'),
    path('procceslocation/', views.process_staff_location, name='process_staff_location'),
    path('procces_userlocation/', views.process_user_location, name='process_user_location'),
    path('ignore_location/', views.ignore_location, name='ignore_location')
]