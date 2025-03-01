from django.apps import AppConfig


class AttendanceAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Attendance_app'

    def ready(self):
        import Attendance_app.signals
