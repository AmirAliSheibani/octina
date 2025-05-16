from datetime import datetime, timedelta
from datetime import timezone
from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL
import jdatetime
from django.db import models
from django.utils import timezone
from django_jalali.db import models as jmodels
from django.db import models
from jalali_date import date2jalali

import uuid
from django.db import models
from django.utils import timezone
from jalali_date import date2jalali
from datetime import timedelta
import uuid


class AttendanceUser(models.Model):
    id = models.CharField(primary_key=True, max_length=36, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_attendance')
    created_date = jmodels.jDateField(auto_now_add=True, null=True, blank=True)
    month = models.PositiveSmallIntegerField(editable=False, default=1)
    year = models.PositiveSmallIntegerField(editable=False, default=1403)
    start = models.TimeField(null=True, blank=True)
    end = models.TimeField(null=True, blank=True)
    job_time = models.DurationField(default=timedelta(0), blank=True)
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    last_info = models.TextField(max_length=800, default=' +', null=True, blank=True)

    in_progress = models.BooleanField(default=False)
    holiday_check = models.BooleanField(default=False)
    overtime_check = models.BooleanField(default=False)
    overtime_duration = models.DurationField(default=timedelta(0), blank=True)
    confirmation = models.BooleanField(null=True, blank=True)

    delay = models.OneToOneField('pricing.Delay', on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='attendance')

    def save(self, *args, **kwargs):
        required_time = kwargs.pop('required_time', None)
        if self.job_time:
            self.job_time = timedelta(seconds=int(self.job_time.total_seconds()))
        if self.end:
            if self.job_time <= timedelta(seconds=0):
                self.job_time = datetime.combine(datetime.min, self.end) - datetime.combine(datetime.min, self.start)

        if self.overtime_check and required_time:
            self.overtime_duration = self.job_time - required_time

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Attendance for {self.user.username} - {self.job_time}"


class AttendanceStatus(models.Model):
    STATUS_CHOICES = [
        ('absent', 'غیبت'),
        ('delay', 'تاخیر'),
        ('overtime', 'اضافه‌کاری'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    detail = models.TextField(blank=True, null=True)  # مثلاً مدت تاخیر، یا توضیحی برای اضافه‌کاری
    created_date = jmodels.jDateTimeField(auto_now_add=True)
    month = models.PositiveSmallIntegerField(null=True)
    year = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return f"{self.user.username} - {self.status} - {self.date}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the month if the object is being created
            self.month = date2jalali(timezone.now().date()).month
            self.year = date2jalali(timezone.now().date()).year
        super().save(*args, **kwargs)


class AbsenceWarning(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="warnings")
    message = models.TextField()
    is_seen = models.BooleanField(default=False)
    created_at = jmodels.jDateField(auto_now_add=True)
    related_status = models.ForeignKey(
        'AttendanceStatus', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='warnings'
    )

    def __str__(self):
        return f"Warning for {self.user.username} - Seen: {self.is_seen}"
