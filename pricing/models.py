from datetime import timedelta

from django.conf import settings
# from django.contrib.auth.models import User
from django.db import models
from Attendance_app.models import AttendanceUser
from django.contrib.auth.models import AbstractUser

from django.conf import settings

User = settings.AUTH_USER_MODEL


class Positions(models.Model):
    positions = models.CharField(max_length=100)
    position_income = models.IntegerField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Positions', blank=True,
                                   null=True)

    def __str__(self):
        return self.positions

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)


class Subscriptions(models.Model):
    mounth = models.SmallIntegerField()
    price = models.IntegerField()
    image = models.ImageField()
    text = models.TextField(max_length=500)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_position = models.ForeignKey(Positions, on_delete=models.SET_NULL, null=True, related_name='poss')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Profile', blank=True,
                                   null=True)
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='subscription')

    def __str__(self):
        return f"{self.profile_position}"

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)


class Income(models.Model):
    USer = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='USer')
    position = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='poSition')
    created_date = models.DateField(auto_created=True, null=True)
    job_time = models.DurationField(default=timedelta(0), blank=True)
    User_income = models.IntegerField(default=0)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_income', blank=True,
                                   null=True)

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)


class CustomUser(AbstractUser):
    created_who = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='created_custom_userss')
    subscription_Date = models.DateField(blank=True, auto_created=True, null=True)
    verified_email = models.BooleanField(default=False)
