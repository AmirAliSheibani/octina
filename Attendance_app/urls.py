from django.urls import path
from . import views

app_name = 'Attendance'

urlpatterns = [
    path('homepage/', views.create_attendance_view, name='home'),
    path('start/', views.start_attendance_view, name='start'),
    path('resultlist/<int:pk>/<int:month>/', views.AttendanceListView.as_view(), name='result_list'),
    path('procces/<str:pk>/', views.process_result_view, name='procces_result'),
    path('result/', views.ShowResult.as_view(), name='result'),
    # path('update-duration/', views.update_duration_view, name='update_duration'),
    path('resultdetail/<int:user>/<int:pk>', views.ShowResult.as_view(), name='result_detail'),
    path('userlist/<int:pk>/<int:month>/', views.staff_user_list, name='user_list'),
    path('download_excel/<int:pk>/<int:month>/', views.download_excel, name='download_excel'),
    path('download_excel_user/<int:pk>/<int:month>/', views.download_excel_user, name='download_excel_user'),
    path('set_location/', views.get_staff_location, name='get_staff_location'),
    path('set_your_location/', views.get_user_location, name='get_user_location'),
    path('procceslocation/', views.process_staff_location, name='process_staff_location'),
    path('procces_userlocation/', views.process_user_location, name='process_user_location'),
    path('no_confirmation_users/', views.no_confirmation_check, name='no_confirmation_check'),
    path('confirm/<int:pk>/', views.accept_confirmation, name='confirm'),
    path('reject/<int:pk>/', views.not_accepted_confirmation, name='reject'),
    path('ignore_location/', views.ignore_location, name='ignore_location'),
    path('info_users/<int:month>', views.in_progress_users, name='info_users'),
    path('', views.restricted_view, name='redirected_view')
]

