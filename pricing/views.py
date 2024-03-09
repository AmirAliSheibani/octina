from datetime import datetime

from django.shortcuts import render, redirect
from django.urls import reverse
from Attendance_app.models import AttendanceUser
from pricing.models import Income, Profile, CustomUser
from django.conf import settings
User = settings.AUTH_USER_MODEL

def process_pricing(request, pk):
    at = AttendanceUser.objects.get(user=request.user, token=pk)
    at_month = at.created_date.month
    # current_month = datetime.now().month


    try:
        income = Income.objects.get(USer=at.user, month=at_month)
        job_time = datetime.combine(datetime.min, at.end) - datetime.combine(datetime.min, at.start)
        inc = round(income.position.profile_position.position_income * (job_time.total_seconds() / 3600), 4)
        income.job_time += at.job_time
        print(at.job_time, "at.job_time")
        print(income.job_time, 'income.job_time')
        print(income.User_income, 'print(income.User_income)')
        income.User_income += inc
        print(income.User_income)
        income.created_by = request.user.created_who
        income.save()
    except:
        income = Income.objects.create(created_date=at.created_date, USer=at.user,
                                       position=Profile.objects.get(user=at.user), job_time=at.job_time)
        income.User_income = income.position.profile_position.position_income * (
                    income.job_time.total_seconds() / 3600)
        print(request.user.is_staff)
        income.created_by = request.user.created_who

        income.save()

    request.session['token'] = pk


    return redirect(reverse('Attendance:result'))





