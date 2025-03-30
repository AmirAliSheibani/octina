from django.urls import path
from . import views

app_name = 'Attendance'
urlpatterns = [
# path('update-duration/', views.update_duration_view, name='update_duration'),
    path('homepage/', views.create_attendance_view, name='home'),
    path('start/', views.start_attendance_view, name='start'),
    path('procces/<str:pk>/', views.process_result_view, name='procces_result'),
    path('result/', views.ShowResult.as_view(), name='result'),
    path('resultdetail/<int:user>/<str:pk>', views.ShowResult.as_view(), name='result_detail'),
    path('resultlist/<int:pk>/<int:month>/<int:year>/', views.AttendanceListView.as_view(), name='result_list'),
    path('download_excel_user/<int:pk>/<int:month>/<int:year>/', views.download_excel_user, name='download_excel_user'),
    path('personal_info/', views.personal_info, name='personal_info'),
    path('holiday_list/', views.list_holidays, name='list_holidays'),
    path('get_vacation/', views.getting_vacation, name='get_vacation'),
    path('warnings/', views.user_warnings_view, name='user_warnings_view'),
    path('all_warnings/', views.all_user_warnings_view, name='all_user_warnings_view'),
    path('delete_user_warning/<int:warning_id>/', views.delete_user_warning, name='delete_user_warning'),
    path('warnings/seen/<int:warning_id>/', views.mark_warning_seen, name='mark_warning_seen'),
    path('', views.restricted_view, name='redirected_view')

]
