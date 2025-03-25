from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from django.core.management.base import BaseCommand

from Attendance_app.models import AttendanceUser, AbsenceRecord

User = get_user_model()

class Command(BaseCommand):
    help = 'Calculate and record absences for the day'

    def handle(self, *args, **options):
        today = now().date()
        present_users = AttendanceUser.objects.filter(created_date=today).values_list('user', flat=True)
        print(present_users)
        absent_users = User.objects.filter(created_who__isnull=False, is_staff=False).exclude(id__in=present_users).values_list('id', flat=True)
        if absent_users:
            absent_record, created = AbsenceRecord.objects.get_or_create(date=today)
            absent_record.absent_users.add(*absent_users)
            print(absent_record.absent_users.all())
            absent_record.save()

