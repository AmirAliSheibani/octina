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


def calculate_income(income, job_time, overtime=None):
    """محاسبه درآمد و اضافه‌کاری بدون تغییر مقدار ماهانه در حالت حقوق ثابت."""

    if income.position.profile_position.monthly:
        # یوزر حقوق ثابت ماهانه دارد، پس فقط اضافه‌کاری حساب شود
        if overtime:
            overtime_income = income.position.profile_position.overtime_position_income * (
                        overtime.total_seconds() / 3600)
            income.surplus += Decimal(overtime_income)  # فقط اضافه‌کاری اضافه شود
    else:
        # یوزر حقوق ساعتی دارد، پس حقوق عادی + اضافه‌کاری حساب شود
        hourly_income = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
        income.user_income += Decimal(hourly_income)
        print(overtime)
        if overtime:
            print('true')
            overtime_income = income.position.profile_position.overtime_position_income * (
                        overtime.total_seconds() / 3600)
            income.surplus += Decimal(overtime_income)
            income.user_income += Decimal(overtime_income)  # برای یوزرهای ساعتی، اضافه‌کاری هم به درآمد کل اضافه شود
        else:
            print('false')

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
    print('***********')
    print('process_pricing')
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

    if income.position.profile_position.monthly:
        income.user_income = income.position.profile_position.position_income

    current_shift = get_shiftwork(income)
    is_holiday_today = at.holiday_check

    # if current_shift and not is_holiday_today:
    #     start_shift_time, end_shift_time = current_shift.work_start_time, current_shift.work_end_time
    #     if start_shift_time < datetime.now().time() < end_shift_time:
    #         if income.position.profile_position.monthly:
    #             # فقط اضافه‌کاری حساب شود
    #             calculate_income(income, job_time, only_overtime=True)
    #         else:
    #             # حقوق عادی + اضافه‌کاری حساب شود
    #             calculate_income(income, job_time)
    #     else:
    #         # خارج از ساعت شیفت = اضافه‌کاری حساب شود
    #         calculate_income(income, job_time, only_overtime=True)
    # else:
    #     # روز تعطیل = اضافه‌کاری حساب شود
    #     calculate_income(income, job_time, only_overtime=True)

    if current_shift and not is_holiday_today:
        if not at.overtime_check:
            print('not overtime')
            if income.position.profile_position.monthly:
                print('pass')
                # فقط اضافه‌کاری حساب شود
                # calculate_income(income, job_time)
            else:
                print("حقوق عادی + اضافه‌کاری حساب شود")
                # حقوق عادی + اضافه‌کاری حساب شود
                calculate_income(income, job_time)
        else:
            # خارج از ساعت شیفت = اضافه‌کاری حساب شود
            print("خارج از ساعت شیفت = اضافه‌کاری حساب شود")
            calculate_income(income, job_time, overtime=at.overtime_duration)
    else:
        # روز تعطیل = اضافه‌کاری حساب شود
        print("روز تعطیل = اضافه‌کاری حساب شود")
        calculate_income(income, job_time,overtime=at.overtime_duration)


    income.job_time += job_time
    income.save()


    request.session['token'] = pk
    return redirect(reverse('Attendance:result'))
