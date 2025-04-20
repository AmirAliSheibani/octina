from datetime import timezone
import jdatetime
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.core.management.base import BaseCommand
from Attendance_app.models import AttendanceUser, AbsenceRecord, AbsenceWarning

User = get_user_model()

class Command(BaseCommand):
    help = 'Calculate and record absences for the day'

    def handle(self, *args, **options):
        current_time = now()
        today = jdatetime.date.fromgregorian(date=current_time.date())

        # پیدا کردن کاربران حاضر
        present_users = AttendanceUser.objects.filter(created_date=today).values_list('user', flat=True)
        print(f'present_users: {len(present_users)}')

        # پیدا کردن کاربران غایب (به‌صورت tuple شامل id و username)
        absent_users = User.objects.filter(
            created_who__isnull=False, is_staff=False
        ).exclude(id__in=present_users).values_list('id', 'username')  # گرفتن ID و یوزرنیم

        if absent_users:
            # جدا کردن فقط IDها برای اضافه شدن به رکورد غیبت
            absent_user_ids = [user[0] for user in absent_users]

            absent_record, created = AbsenceRecord.objects.get_or_create(created_date=today)
            absent_record.absent_users.add(*absent_user_ids)
            absent_record.save()
            print(f'absent_record: {absent_record}')

            # بررسی تعداد غیبت‌ها در ماه جاری برای هر کاربر غایب
            current_month = today.month
            current_year = today.year

            for user_id, username in absent_users:
                absence_count = AbsenceRecord.objects.filter(
                    absent_users=user_id, month=current_month, year=current_year
                ).count()

                if absence_count > 2:
                    message = f"شما بیش از 2 بار در این ماه غایب بوده‌اید! لطفاً علت را توضیح دهید."
                    AbsenceWarning.objects.create(user_id=user_id, message=message)

                    # ارسال پیام برای مدیر
                    user = User.objects.get(id=user_id)
                    if user.created_who:  # یعنی کارمند یک مدیر داره
                        manager_message = f"کارمند {username} بیش از 2 بار در این ماه غایب بوده است."
                        AbsenceWarning.objects.create(user=user.created_who, message=manager_message)

