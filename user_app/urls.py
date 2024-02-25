from django.urls import path
from . import views

app_name= 'user'

urlpatterns = [
    path('register/', views.UserRegisterView, name='register'),
    path('login/', views.UserLoginView, name='login'),
    path('logout/', views.logoutUser, name='logout'),
    path('sendemail/<str:email>/', views.email_form_context, name='send_email'),
    path('chek_your_email/', views.check_verified_email, name='verified_email'),
    path('get_email_pass/', views.GetEmail, name='get_email_pass'),
    path('sendpasscode/<str:email>/', views.send_password_code, name='send_passcode_email'),
    path('pass_code/<str:email>/', views.check_password_code, name='pass_code'),
    path('change_password/<str:email>/<str:code>/', views.change_password, name='change_password'),

]