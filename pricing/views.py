from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.urls import reverse
from Attendance_app.models import AttendanceUser
from Attendance_app.utils import get_day_mapping
from pricing.models import Income, Profile, CustomUser, Holidays
from django.conf import settings
import datetime as d

User = settings.AUTH_USER_MODEL
from decimal import Decimal

from datetime import datetime, timedelta
from decimal import Decimal
from django.shortcuts import redirect, reverse
from django.db.models import Q


def calculate_income(income, job_time):
    """محاسبه درآمد و اضافه‌کاری."""
    hourly_income = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
    overtime_income = income.position.profile_position.overtime_position_income * (job_time.total_seconds() / 3600)

    income.user_income += Decimal(hourly_income)
    income.surplus += Decimal(overtime_income)
    income.user_income += Decimal(overtime_income)
    income.save()


def is_holiday():
    """بررسی اینکه آیا روز جاری تعطیل است یا خیر."""
    return Holidays.objects.filter(date=datetime.now()).exists()


def get_shiftwork(income):
    """دریافت شیفت کاری مربوط به روز جاری."""
    day_mapping = get_day_mapping()
    current_day_number = datetime.now().weekday()
    reversed_day_number = day_mapping[current_day_number]
    return income.position.profile_position.shift_work.filter(work_days__day_of_week=reversed_day_number).last()


def process_pricing(request, pk):
    at = AttendanceUser.objects.get(user=request.user, token=pk)
    at_month, at_year = at.created_date.month, at.created_date.year
    job_time = datetime.combine(datetime.min, at.end) - datetime.combine(datetime.min, at.start)

    income, created = Income.objects.get_or_create(
        user=at.user, month=at_month, year=at_year,
        defaults={
            "created_date": at.created_date,
            "position": Profile.objects.get(user=at.user),
            "job_time": at.job_time,
            "created_by": request.user.created_who
        }
    )

    if created and income.position.profile_position.monthly:
        income.user_income = income.position.profile_position.position_income

    current_shift = get_shiftwork(income)
    is_holiday_today = is_holiday()

    if current_shift and not is_holiday_today:
        start_shift_time, end_shift_time = current_shift.work_start_time, current_shift.work_end_time
        if start_shift_time < datetime.now().time() < end_shift_time:
            if not income.position.profile_position.monthly:
                calculate_income(income, job_time)
        else:
            calculate_income(income, job_time)
    else:
        calculate_income(income, job_time)

    income.job_time += job_time
    income.save()

    request.session['token'] = pk
    return redirect(reverse('Attendance:result'))
