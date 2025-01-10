from datetime import datetime, timedelta
from datetime import timezone
from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
import jdatetime
from django.db import models
from django.utils import timezone

from django.db import models
from django_jalali.db import models as jmodels
from jalali_date import date2jalali


class AttendanceUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='user_attendance')
    created_date = jmodels.jDateField(auto_created=True, null=True, blank=True)
    month = models.PositiveSmallIntegerField(default=None, null=True)
    year = models.PositiveSmallIntegerField(default=None, null=True)
    start = models.TimeField(auto_now=False, null=True, blank=True)
    end = models.TimeField(auto_now=False, null=True, blank=True)
    job_time = models.DurationField(default=timedelta(0), blank=True)
    token = models.CharField(max_length=100, default=user)
    last_info = models.TextField(max_length=800, default=' +', null=True, blank=True)
    in_progress = models.BooleanField(default=False)

    holiday_check = models.BooleanField(default=False)
    overtime_check = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='created_by_AttendanceUser')
    confirmation = models.BooleanField(default=None, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the month if the object is being created
            self.month = date2jalali(timezone.now().date()).month
            self.year = date2jalali(timezone.now().date()).year
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.job_time}"
