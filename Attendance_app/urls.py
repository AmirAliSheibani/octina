from django.urls import path
from . import views

app_name = 'Attendance'

urlpatterns = [
    path('homepage/', views.create_attendance_view, name='home'),
    path('start/', views.start_attendance_view, name='start'),
    path('resultlist/<int:pk>', views.AttendanceListView.as_view(), name='result_list'),
    path('procces/<str:pk>/', views.process_result_view, name='procces_result'),
    path('result/', views.ShowResult.as_view(), name='result'),
    path('update-duration/', views.update_duration_view, name='update_duration'),
    path('resultdetail/<int:user>/<int:pk>', views.ShowResult.as_view(), name='result_detail'),
    path('userlist/<int:pk>', views.staff_user_list, name='user_list'),
    path('', views.restricted_view, name='redirected_view')
]

