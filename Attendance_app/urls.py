from django.urls import path
from . import views

app_name = 'Attendance'

urlpatterns = [
    path('homepage/', views.create_attendance_view, name='home'),
    path('start/', views.start_attendance_view, name='start'),
    path('resultlist/<int:pk>/<int:month>/', views.AttendanceListView.as_view(), name='result_list'),
    path('procces/<str:pk>/', views.process_result_view, name='procces_result'),
    path('result/', views.ShowResult.as_view(), name='result'),
    path('update-duration/', views.update_duration_view, name='update_duration'),
    path('resultdetail/<int:user>/<int:pk>', views.ShowResult.as_view(), name='result_detail'),
    path('userlist/<int:pk>/<int:month>/', views.staff_user_list, name='user_list'),
    path('download_excel/<int:pk>/<int:month>/', views.download_excel, name='download_excel'),
    path('download_excel_user/<int:pk>/<int:month>/', views.download_excel_user, name='download_excel_user'),
    path('/', views.restricted_view, name='redirected_view')
]

