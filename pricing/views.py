from datetime import datetime, timezone

from django.shortcuts import render, redirect
from django.urls import reverse
from Attendance_app.models import AttendanceUser
from pricing.models import Income, Profile, CustomUser, Holidays
from django.conf import settings
import datetime as d

User = settings.AUTH_USER_MODEL
from decimal import Decimal


def process_pricing(request, pk):
    at = AttendanceUser.objects.get(user=request.user, token=pk)
    at_month = at.created_date.month
    # current_month = datetime.now().month

    try:

        income = Income.objects.get(user=at.user, month=at_month, year=at.created_date.year)
        job_time = datetime.combine(datetime.min, at.end) - datetime.combine(datetime.min, at.start)
        shiftwork = income.position.profile_position.shift_work

        # Get the current day of the week (0 for Monday, 1 for Tuesday, and so on)
        day_mapping = {
            5: 0,  # Saturday
            6: 1,  # Sunday
            0: 2,  # Monday
            1: 3,  # Tuesday
            2: 4,  # Wednesday
            3: 5,  # Thursday
            4: 6,  # Friday
        }

        current_day_number = datetime.now().weekday()
        reversed_day_number = day_mapping[current_day_number]
        check_holidays = datetime.now()
        try:
            Holidays.objects.get(date=check_holidays)
            check_holidays = True
        except Holidays.DoesNotExist:
            check_holidays = False

        print(current_day_number, reversed_day_number)

        # Get the corresponding ShiftWork object for the current day
        current_shift = shiftwork.filter(work_days__day_of_week=reversed_day_number).last()
        print(current_shift)
    
        if current_shift is not None and not check_holidays:
            start_shift_time = current_shift.work_start_time
            end_shift_time = current_shift.work_end_time
            print(d.datetime.now().time())
            income.save()

            if start_shift_time < d.datetime.now().time() < end_shift_time:
                if income.position.profile_position.monthly:
                    pass
                else:
                    inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                    income.user_income += Decimal(inc)
                    print('income.user_income += Decimal(inc)')
                    print('income.surplus += Decimal(inc) income.user_income += Decimal(inc) ')
                income.save()

            else:
                if income.position.profile_position.monthly:
                    pass
                else:
                    inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                    income.user_income += Decimal(inc)
                surplus_inc = income.position.profile_position.overtime_position_income * (job_time.total_seconds() / 3600)
                income.surplus += Decimal(surplus_inc)
                income.user_income += Decimal(surplus_inc)
                income.save()

        else:
            if income.position.profile_position.monthly:
                pass
            else:
                inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                income.user_income += Decimal(inc)
            surplus_inc = income.position.profile_position.overtime_position_income * (
                        job_time.total_seconds() / 3600)
            income.surplus += Decimal(surplus_inc)
            income.user_income += Decimal(surplus_inc)
            income.save()
            print('income.surplus += Decimal(inc) income.user_income += Decimal(inc)1111 ')

        income.job_time += at.job_time
        income.created_by = request.user.created_who
        income.save()
    except Income.DoesNotExist:
        income = Income.objects.create(created_date=at.created_date, user=at.user,
                                       position=Profile.objects.get(user=at.user), job_time=at.job_time)

        print(request.user.is_staff)
        income.created_by = request.user.created_who
        if income.position.profile_position.monthly:
            income.user_income = income.position.profile_position.position_income


        job_time = datetime.combine(datetime.min, at.end) - datetime.combine(datetime.min, at.start)
        shiftwork = income.position.profile_position.shift_work

        # Get the current day of the week (0 for Monday, 1 for Tuesday, and so on)
        day_mapping = {
            5: 0,  # Saturday
            6: 1,  # Sunday
            0: 2,  # Monday
            1: 3,  # Tuesday
            2: 4,  # Wednesday
            3: 5,  # Thursday
            4: 6,  # Friday
        }

        current_day_number = datetime.now().weekday()
        reversed_day_number = day_mapping[current_day_number]
        check_holidays = datetime.now()
        try:
            Holidays.objects.get(date=check_holidays)
            check_holidays = True
        except Holidays.DoesNotExist:
            check_holidays = False

        print(current_day_number, reversed_day_number)

        # Get the corresponding ShiftWork object for the current day
        current_shift = shiftwork.filter(work_days__day_of_week=reversed_day_number).last()
        print(current_shift)

        if current_shift is not None and not check_holidays:
            start_shift_time = current_shift.work_start_time
            end_shift_time = current_shift.work_end_time
            print(d.datetime.now().time())
            income.save()

            if start_shift_time < d.datetime.now().time() < end_shift_time:
                if income.position.profile_position.monthly:
                    pass
                else:
                    inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                    income.user_income += Decimal(inc)
                print('income.user_income += Decimal(inc)')
                print('income.surplus += Decimal(inc) income.user_income += Decimal(inc) ')
                income.save()
            else:
                if income.position.profile_position.monthly:
                    pass
                else:
                    inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                    income.user_income += Decimal(inc)
                surplus_inc = income.position.profile_position.overtime_position_income * (job_time.total_seconds() / 3600)
                income.surplus += Decimal(surplus_inc)
                income.user_income += Decimal(surplus_inc)
                income.save()

        else:
            if income.position.profile_position.monthly:
                pass
            else:
                inc = income.position.profile_position.position_income * (job_time.total_seconds() / 3600)
                income.user_income += Decimal(inc)
            surplus_inc = income.position.profile_position.overtime_position_income * (
                        job_time.total_seconds() / 3600)
            income.surplus += Decimal(surplus_inc)
            income.user_income += Decimal(surplus_inc)
            income.save()


        income.save()
    request.session['token'] = pk

    return redirect(reverse('Attendance:result'))
