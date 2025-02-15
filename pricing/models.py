from datetime import timedelta, datetime

from django.conf import settings
# from django.contrib.auth.models import User
from django.db import models
from Attendance_app.models import AttendanceUser
from django.contrib.auth.models import AbstractUser

from django.conf import settings
import jdatetime
from django.db import models
from django.utils import timezone

User = settings.AUTH_USER_MODEL
from django_jalali.db import models as jmodels
from jalali_date import date2jalali
from decimal import Decimal


# class JalaliDateField(models.DateField):
#     def from_db_value(self, value, expression, connection):
#         if value is None:
#             return value
#         return date2jalali(value)
#
#     def to_python(self, value):
#         if isinstance(value, tuple):
#             return value
#         if value is None:
#             return value
#         return date2jalali(value)
#
#     def get_prep_value(self, value):
#         if value is None:
#             return value
#         return value.to_gregorian()




class Holidays(models.Model):
    date = jmodels.jDateTimeField(auto_created=True)
    name = models.CharField(max_length=80, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Holidays', blank=True,
                                   null=True)

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)


class VacationType(models.Model):
    name_type = models.CharField(max_length=80)
    Limitation = models.SmallIntegerField(null=True, blank=True)
    get_income = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.name_type}'


class Vacation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vacations')
    date = models.DateField(auto_now_add=True)
    vacation_type = models.ForeignKey(VacationType, on_delete=models.CASCADE, related_name='vacations', null=True)
    reason = models.CharField(max_length=125)
    check_by_employer = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.vacation_type.name_type}'


class ShiftWork(models.Model):
    work_start_time = models.TimeField(null=True)
    work_end_time = models.TimeField(null=True)
    # Every day, working hours may be different from other days of the week
    work_days = models.ManyToManyField('Day', related_name='Days')
    required_time = models.DurationField(default=timedelta(0), blank=True)
    name = models.CharField(max_length=70, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_shift_works', blank=True,
                                   null=True)

    def __str__(self):
        return f'{self.name}'

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)



    def save(self, *args, **kwargs):
        self.required_time = datetime.combine(datetime.min, self.work_end_time) - datetime.combine(datetime.min,
                                                                                                   self.work_start_time)
        print(self.required_time)
        print(1)
        super().save(*args, **kwargs)


class Positions(models.Model):
    positions = models.CharField(max_length=100)
    position_income = models.IntegerField()
    # Every employee must be in the company on certain days and these days are determined here.
    work_days = models.ManyToManyField('Day', related_name='days')
    # If he is supposed to work on unspecified days, then it is considered overtime.

    shift_work = models.ManyToManyField('ShiftWork', related_name='Shift_work')

    # Also, according to the series of working hours, they must be inside the company,
    # and being inside the company more than those working hours is considered overtime
    overtime_position_income = models.IntegerField(null=True, blank=True)
    monthly = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Positions', blank=True,
                                   null=True)

    def __str__(self):
        return self.positions


class Day(models.Model):
    WEEKDAYS = (
        (0, 'شنبه'),
        (1, 'یک‌شنبه'),
        (2, 'دوشنبه'),
        (3, 'سه‌شنبه'),
        (4, 'چهارشنبه'),
        (5, 'پنج‌شنبه'),
        (6, 'جمعه'),
    )
    day_of_week = models.PositiveIntegerField(choices=WEEKDAYS)

    def __str__(self):
        return self.get_day_of_week_display()


class Subscriptions(models.Model):
    mounth = models.SmallIntegerField()
    price = models.IntegerField()
    image = models.ImageField()
    text = models.TextField(max_length=500)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='possit')
    profile_position = models.ForeignKey(Positions, on_delete=models.CASCADE, related_name='poss')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_by_Profile', blank=True,
                                   null=True)
    subscription = models.ForeignKey(Subscriptions, on_delete=models.CASCADE, blank=True, null=True,
                                     related_name='subscription')
    vacation = models.ManyToManyField(Vacation, related_name='vacation_profile', blank=True)

    def __str__(self):
        return f"{self.profile_position}"

    def save_model(self, request, obj, form, change):
        self.created_by = request.user
        super().save_model(request, obj, form, change)


class Income(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1, related_name='user_incomes')
    position = models.ForeignKey(Profile, on_delete=models.CASCADE, blank=True, null=True, related_name='positions')
    created_date = jmodels.jDateField(auto_created=True, null=True, blank=True)
    month = models.PositiveSmallIntegerField()
    year = models.PositiveSmallIntegerField(default=None, null=True)
    job_time = models.DurationField(default=timezone.timedelta, blank=True)
    user_income = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    surplus = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_incomes', blank=True,
                                   null=True)

    def __str__(self):
        return f'{self.user_income}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the month if the object is being created
            self.month = date2jalali(timezone.now().date()).month
            self.year = date2jalali(timezone.now().date()).year

        # جلوگیری از مقدار منفی برای درآمد، اضافه‌کاری و زمان کار
        self.user_income = max(Decimal('0.00'), self.user_income)
        self.surplus = max(Decimal('0.00'), self.surplus)
        self.job_time = max(timedelta(0), self.job_time)
        super().save(*args, **kwargs)


class NoneInProgress(models.Model):
    user = models.ManyToManyField(User, related_name='nonprogres', blank=True)
    created_date = jmodels.jDateField(auto_created=True, null=True, blank=True)
    month = models.PositiveSmallIntegerField( null=True)
    year = models.PositiveSmallIntegerField(default=None, null=True)

    def __str__(self):
        return f'{self.created_date} - {self.month}'

    def save(self, *args, **kwargs):
        if not self.pk:  # Only set the month if the object is being created
            self.month = date2jalali(timezone.now().date()).month
            self.year = date2jalali(timezone.now().date()).year
        super().save(*args, **kwargs)


class CustomUser(AbstractUser):
    created_who = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                    related_name='created_custom_userss')
    absent = models.BooleanField(default=True)
    subscription_Date = jmodels.jDateField(blank=True, null=True)
    verified_email = models.BooleanField(default=False)
