from datetime import datetime, timedelta
from datetime import timezone
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
User = settings.AUTH_USER_MODEL
class AttendanceUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='user_attendance')
    created_date = models.DateField(auto_now=False, null=True)
    start = models.TimeField(auto_now=False, null=True, blank=True)
    end = models.TimeField(auto_now=False, null=True, blank=True)
    job_time = models.DurationField(default=timedelta(0), blank=True)
    token = models.CharField(max_length=1000, default=user)
    last_info = models.TextField(max_length=1000, default=' +', null=True, blank=True)
    in_progress = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='created_by_AttendanceUser')








