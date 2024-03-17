import math
import uuid

import jdatetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta
from geopy.distance import geodesic
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import AttendanceUser
from .mixin import CustomizedRquirementLogin
from django.contrib.auth.decorators import login_required
from pricing.models import Profile, User, CustomUser, Income, Location
from .form import PositionForm
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
# exel

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from django.http import HttpResponse
from django.db.models import Q
from django.db.models import Q


def get_staff_location(request):
    return render(request, 'Attendance_app/staff_location.html')


def get_user_location(request):
    return render(request, 'Attendance_app/user_location.html')


@csrf_exempt
def process_user_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        user = request.user

        # موقعیت مرجع
        location = Location.objects.get(created_by=request.user.created_who, active=True)
        reference_latitude = location.latitude
        reference_longitude = location.longitude
        #
        # # موقعیت جدید
        # new_latitude = 35.123456789
        # new_longitude = 51.987654321
        #
        # # محاسبه فاصله بین دو موقعیت
        distance = geodesic((reference_latitude, reference_longitude), (latitude, longitude)).meters
        #
        # بررسی آیا فاصله کمتر از 50 متر است
        date = datetime.now().date()
        at = AttendanceUser.objects.get(user=user, created_date=date)
        start = datetime.now().time()
        if distance < 50:
            print("موقعیت در فاصله کمتر از 50 متر است")
            at.confirmation = True
            at.start = start
            at.save()
        else:
            print("موقعیت در فاصله بیشتر از 50 متر است")
            at.confirmation = False
            at.start = start
            at.save()
        print(f'{latitude},{longitude}')
        return redirect(reverse('Attendance:start'))
    else:
        return HttpResponseNotAllowed(['POST'])


def ignore_location(request):
    user = request.user
    date = datetime.now().date()
    at = AttendanceUser.objects.get(user=user, created_date=date)
    start = datetime.now().time()
    at.confirmation = False
    at.start = start
    at.save()
    return redirect(reverse('Attendance:start'))


@csrf_exempt
def process_staff_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        user = request.user
        location = Location.objects.create(longitude=longitude, latitude=latitude, created_by=user, active=True)
        # return HttpResponse(f'{latitude},{longitude}')
        return redirect(reverse('Attendance:redirected_view'))
    else:
        return HttpResponseNotAllowed(['POST'])


@login_required
def restricted_view(request):
    user = request.user

    now = timezone.now().date()
    jalali_date = jdatetime.date.fromgregorian(date=now)
    # # Access the Jalali year, month, and day
    # jalali_year = jalali_date.year
    # jalali_month = jalali_date.month
    # jalali_day = jalali_date.day

    # Check if the subscription date is today or in the past
    if user.subscription_Date and user.subscription_Date <= jalali_date:
        # Disable the user or perform any other desired action
        user.is_active = False
        user.save()

        # Redirect or display an appropriate message to the user
        return HttpResponse("Your subscription has expired. Please contact support.")
    try:
        # in_progress=True:
        # user is still working
        at = AttendanceUser.objects.get(user=user, in_progress=True)
        # print("at = AttendanceUser.objects.get(user=request.user, in_progress=True)")
        return redirect(reverse('Attendance:start'))
    except AttendanceUser.DoesNotExist:
        return redirect('Attendance:home')


class AttendanceListView(CustomizedRquirementLogin, ListView):
    model = AttendanceUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        month = self.kwargs['month']
        MONTH_NAMES = {
            1: 'فروردین',
            2: 'اردیبهشت',
            3: 'خرداد',
            4: 'تیر',
            5: 'مرداد',
            6: 'شهریور',
            7: 'مهر',
            8: 'آبان',
            9: 'آذر',
            10: 'دی',
            11: 'بهمن',
            12: 'اسفند',
        }

        context['months'] = MONTH_NAMES

        try:
            att = AttendanceUser.objects.filter(user_id=pk, month=month)
            print(month, 'from line75 AttendanceListView')
            context['user'] = CustomUser.objects.get(id=pk)
            at = att.first()
            at_month = at.created_date.month
            job_time = []

            try:
                income = Income.objects.get(USer=at.user, month=at_month)

            except Income.DoesNotExist:
                profile = Profile.objects.get(user=at.user)
                income = Income.objects.create(created_date=at.created_date, User=at.user,
                                               position=profile, job_time=at.job_time)
                income.User_income = profile.position_income * (income.job_time.total_seconds() / 3600)
                income.created_by = self.request.user.created_who
                income.save()

            objects = att
            inc = income.position.profile_position.position_income
            results = []
            for obj in objects:
                result = inc * (obj.job_time.total_seconds() / 3600)
                results.append(round(result, 4))
                job = str(obj.job_time)
                if 'day' in job:
                    job_time.append(job.replace("day", "روز")[:14])
                else:
                    job_time.append(job[:7])

            # Pass the objects and results to the template context

            context["object"] = zip(att, results, job_time)
            context['income'] = income
            context['month'] = month

        except:
            context["object"] = None
            context['user'] = CustomUser.objects.get(id=pk)

            context['income'] = None
            context['month'] = month

        return context

    # def get_fieldsets(self, request, obj=None):
    #
    #     if not request.user.is_superuser:
    #         if not obj:
    #             return self.add_fieldsets
    #         fieldsets = [
    #
    #             (None, {"fields": ("username", "password")}),
    #             (_("Personal info"), {"fields": ("first_name", "last_name", "email")})
    #         ]
    #         return fieldsets


@login_required
def download_excel_user(request, pk, month):
    user = CustomUser.objects.get(id=pk)
    positions = Profile.objects.get(user=user)
    attendances = AttendanceUser.objects.filter(user=user, month=month)
    income = Income.objects.get(USer=user, month=month)
    MONTH_NAMES = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند',
    }

    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active

    # Set month name
    month_name = MONTH_NAMES.get(month)
    sheet["A1"] = f"Month: {month_name}"
    sheet.merge_cells("A1:F1")
    sheet["A1"].font = Font(bold=True)

    # Set table headers
    headers = ["First Name", "Last Name", "Position", "Total Working Time", "Price", "Total Price"]
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        cell = sheet[f"{col_letter}2"]
        cell.value = header
        cell.font = Font(bold=True)
    job_time = []
    objects = attendances

    for obj in objects:
        job = str(obj.job_time)
        if 'day' in job:
            job_time.append(job.replace("day", "روز")[:14])
        else:
            job_time.append(job[:7])
    # Write table data
    row_num = 3
    objects = zip(attendances, job_time)
    for attendance, job_tim in objects:
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        sheet[f"C{row_num}"] = positions.profile_position.positions  # Extract the position attribute
        sheet[f"D{row_num}"] = job_tim
        inc = income.position.profile_position.position_income * (attendance.job_time.total_seconds() / 3600)
        sheet[f"E{row_num}"] = round(inc, 4)
        sheet[f"F{row_num}"] = income.User_income
        row_num += 1

    # Set response content type
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # Provide a filename for the Excel file
    response["Content-Disposition"] = f"attachment; filename={user.username}_info.xlsx"

    # Save the workbook to the response
    workbook.save(response)
    return response


def staff_user_list(request, pk, month):
    if not request.user.is_staff:
        return redirect(reverse('Attendance:redirected_view'))
    MONTH_NAMES = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند',
    }

    if not request.user.is_superuser:
        users = CustomUser.objects.filter(created_who=request.user)
        # positions = Profile.objects.filter(created_by=request.user)
        income = Income.objects.filter(USer__in=users, month=month).order_by('User_income')
        no_income_users = users.exclude(id__in=income.values_list('USer_id', flat=True))
        attendances = AttendanceUser.objects.filter(user__in=users, month=month)
    else:
        users = CustomUser.objects.filter(created_who__isnull=False).order_by('username')
        # positions = Profile.objects.all()
        income = Income.objects.filter(USer__in=users, month=month).order_by('User_income')
        no_income_users = users.exclude(id__in=income.values_list('USer_id', flat=True))
        attendances = AttendanceUser.objects.filter(user__in=users, month=month)

    job_time = []
    objects = attendances
    if users is None:
        return HttpResponse('شما هیچ یوزری برای نمایش ندارید!')
    if income is None:
        return HttpResponse('یوزر های شما هیچ درآمدی نداشتند!')

    if objects is None:
        return HttpResponse('یوزر های شما هیچ ورود و خروجی نداشتند!')

    for obj in objects:
        job = str(obj.job_time)
        if 'day' in job:
            job_time.append(job.replace("day", "روز")[:14])
        else:
            job_time.append(job[:7])
    data = []
    for income_entry in income:
        user = income_entry.USer
        attendance = attendances.filter(user=user).first()

        data.append((user, attendance, income_entry))
    last_name_filter = request.GET.get('last_name_filter')
    job_time_filter = request.GET.get('job_time_filter')
    income_filter = request.GET.get('income_filter')

    if last_name_filter:
        data = [entry for entry in data if entry[0].last_name.startswith(last_name_filter)]

    if job_time_filter:
        if job_time_filter == 'smaller':
            data = sorted(data, key=lambda entry: entry[3].job_time)
        elif job_time_filter == 'greater':
            data = sorted(data, key=lambda entry: entry[3].job_time, reverse=True)

    if income_filter:
        if income_filter == 'smaller':
            data = sorted(data, key=lambda entry: entry[3].User_income)
        elif income_filter == 'greater':
            data = sorted(data, key=lambda entry: entry[3].User_income, reverse=True)

    return render(request, 'Attendance_app/AdminUserLlist.html',
                  {'object': data, 'checkincome': no_income_users,
                   'noIncome': no_income_users,
                   'months': MONTH_NAMES, 'month': month})


def no_confirmation_check(request):
    if request.user.is_staff:
        users = CustomUser.objects.filter(created_who=request.user)
        no_confirmation = AttendanceUser.objects.filter(
            Q(user__in=users) & (Q(confirmation=False) | Q(confirmation=None)))
        return render(request, 'Attendance_app/confirmation_user.html', {'no_confirmation': no_confirmation})
    else:
        return redirect(reverse('Attendance:redirected_view'))


def accept_confirmation(request, pk):
    if not request.user.is_staff:
        return redirect(reverse('Attendance:redirected_view'))
    at = AttendanceUser.objects.get(pk=pk)
    at.confirmation = True
    at.save()
    return redirect(reverse('Attendance:no_confirmation_check'))


def not_accepted_confirmation(request, pk):
    if not request.user.is_staff:
        return redirect(reverse('Attendance:redirected_view'))
    at = AttendanceUser.objects.get(pk=pk)
    at.delete()
    return redirect(reverse('Attendance:no_confirmation_check'))


@login_required
def download_excel(request, pk, month):
    if not request.user.is_staff:
        return redirect(reverse('Attendance:redirected_view'))
    if not request.user.is_superuser:
        users = CustomUser.objects.filter(created_who=request.user)
        # positions = Profile.objects.filter(created_by=request.user)
        attendances = AttendanceUser.objects.filter(user__in=users, month=month)
        income = Income.objects.filter(USer__in=users, month=month)
    else:
        users = CustomUser.objects.filter(created_who__isnull=False).order_by('username')
        # positions = Profile.objects.all()
        attendances = AttendanceUser.objects.filter(user__in=users, month=month)
        income = Income.objects.filter(USer__in=users, month=month)

    no_income_users = users.exclude(id__in=income.values_list('USer_id', flat=True))
    # for user in users:
    #     try:
    #         att = attendances.get(user=user)
    #     except:
    #         users = users.exclude(pk=user.pk)
    profile_position = getattr(users, 'possit', None).profile_position if hasattr(users, 'possit') else None
    positions = str(profile_position) if profile_position else ''

    # Create an Excel workbook and sheet
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    MONTH_NAMES = {
        1: 'فروردین',
        2: 'اردیبهشت',
        3: 'خرداد',
        4: 'تیر',
        5: 'مرداد',
        6: 'شهریور',
        7: 'مهر',
        8: 'آبان',
        9: 'آذر',
        10: 'دی',
        11: 'بهمن',
        12: 'اسفند',
    }

    # Set month name
    month_name = MONTH_NAMES.get(month)
    sheet["A1"] = f"Month: {month_name}"
    sheet.merge_cells("A1:E1")
    sheet["A1"].font = Font(bold=True)

    # Set table headers
    headers = ["First Name", "Last Name", "Position", "Total Working Time", "Total Price"]
    for col_num, header in enumerate(headers, 1):
        col_letter = get_column_letter(col_num)
        cell = sheet[f"{col_letter}2"]
        cell.value = header
        cell.font = Font(bold=True)
    job_time = []
    # مرتب‌سازی لیست attendances بر اساس نام کاربر
    # attendances = sorted(attendances, key=lambda a: a.user.username)

    for obj in attendances:
        job = str(obj.job_time)
        if 'day' in job:
            job_time.append(job.replace("day", "روز")[:14])
        else:
            job_time.append(job[:7])
    # Write table data
    row_num = 3

    # users = sorted(users, key=lambda u: u.username)
    # # مرتب‌سازی لیست income بر اساس نام کاربر
    # income = sorted(income, key=lambda i: i.USer.username)
    # Write table data
    row_num = 3
    data = []
    for income_entry in income:
        user = income_entry.USer

        data.append((user, income_entry))

    for (user, user_income), w in zip(data, job_time):
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        profile_position = getattr(user, 'possit', None).profile_position if hasattr(user, 'possit') else None
        sheet[f"C{row_num}"] = str(profile_position) if profile_position else ''
        sheet[f"D{row_num}"] = str(w)
        sheet[f"E{row_num}"] = str(user_income.User_income)
        row_num += 1

    # Apply styles
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    for user in no_income_users:
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        profile_position = getattr(user, 'possit', None).profile_position if hasattr(user, 'possit') else None
        sheet[f"C{row_num}"] = str(profile_position) if profile_position else ''
        sheet[f"A{row_num}"].fill = red_fill
        sheet[f"B{row_num}"].fill = red_fill
        sheet[f"C{row_num}"].fill = red_fill
        row_num += 1

    # Set response content type
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # Provide a filename for the Excel file
    response["Content-Disposition"] = f"attachment; filename={request.user.username}_users.xlsx"

    # Save the workbook to the response
    workbook.save(response)

    return response


import re


@login_required
def result_detail(request, pk):
    at = AttendanceUser.objects.get(id=pk)
    at_month = at.created_date.month
    starts = []
    ends = []
    try:
        income = Income.objects.get(USer=at.user, month=at_month)
        print('from try of result_detail')
    except:
        income = Income.objects.create(created_date=at.created_date, USer=at.user,
                                       position=Profile.objects.get(user=at.user), job_time=at.job_time)
        income.User_income = income.position.profile_position.position_income * (
                income.job_time.total_seconds() / 3600)
        print(request.user.is_staff)
        income.created_by = request.user.created_who
        income.save()

    pattern = r"start=(\d{2}:\d{2}:\d{2}), end=(\d{2}:\d{2}:\d{2})"
    matches = re.findall(pattern, at.last_info)

    for match in matches:
        start, end = match
        starts.append(start)
        ends.append(end)

    zipped_times = zip(starts, ends)

    return render(request, 'Attendance_app/result.html', {'zipped_times': zipped_times, 'income': income})


# index
@login_required
def create_attendance_view(request):
    position = Profile.objects.get(user=request.user)
    now = timezone.now()
    month = jdatetime.date.fromgregorian(date=now.date()).month
    # month = timezone.now().month

    try:
        income = Income.objects.get(USer=request.user, month=month).User_income

    except:
        income = 'خالی'

    at = None
    if request.user.is_staff:
        print(11121)
        in_progress_users = []
        non_progress_users = []
        users = CustomUser.objects.filter(created_who=request.user)
        at = AttendanceUser.objects.filter(
            Q(user__in=users) & (Q(confirmation=False) | Q(confirmation=None)))
        attendance_users = AttendanceUser.objects.filter(user__in=users)
        for attendance in attendance_users:
            print("attendance in attendance_users")

            if attendance.in_progress:
                if attendance.user not in in_progress_users and attendance.user not in non_progress_users:
                    in_progress_users.append(attendance.user)
                    print("in_progress_users.append(attendance.user)")
            else:
                if attendance.user not in in_progress_users and attendance.user not in non_progress_users:
                    print("non_progress_users.append(attendance.user)")
                    non_progress_users.append(attendance.user)

        non_progress_users += users.exclude(username__in=in_progress_users).exclude(username__in=non_progress_users)

        return render(request, 'Attendance_app/index.html',
                      {'position': position, 'income': income, 'month': month, 'no_confirmation_users': at,
                       "in_progress_users": in_progress_users, "non_progress_users": non_progress_users,
                       "users": users})

    return render(request, 'Attendance_app/index.html',
                  {'position': position, 'income': income, 'month': month})


def in_progress_users(request, month):
    if request.user.is_staff:
        MONTH_NAMES = {
            1: 'فروردین',
            2: 'اردیبهشت',
            3: 'خرداد',
            4: 'تیر',
            5: 'مرداد',
            6: 'شهریور',
            7: 'مهر',
            8: 'آبان',
            9: 'آذر',
            10: 'دی',
            11: 'بهمن',
            12: 'اسفند',
        }
        in_progress_users = []
        non_progress_users = []
        users = CustomUser.objects.filter(created_who=request.user)

        attendance_users = AttendanceUser.objects.filter(user__in=users)
        for attendance in attendance_users:
            print("attendance in attendance_users")
            if attendance.in_progress:
                if attendance.user not in in_progress_users and attendance.user not in non_progress_users:
                    in_progress_users.append(attendance.user)
                    print("in_progress_users.append(attendance.user)")
            else:
                if attendance.user not in in_progress_users and attendance.user not in non_progress_users:
                    print("non_progress_users.append(attendance.user)")
                    non_progress_users.append(attendance.user)

        non_progress_users += users.exclude(username__in=in_progress_users).exclude(username__in=non_progress_users)
        return render(request, 'Attendance_app/in_progress_users.html',
                      {'in_progress_users': in_progress_users, 'non_progress_users': non_progress_users, 'month':month})
    return redirect(reverse('Attendance:redirected_view'))


@login_required
def start_attendance_view(request):
    try:
        location = Location.objects.get(created_by=request.user.created_who, active=True)
        print('location = True')
    except Location.DoesNotExist:
        location = False
        print('location = False')
    start = datetime.now().time()
    date = datetime.now().date()
    confirmation = False
    user_id = request.user.id

    # ارسال شناسه کاربر به کانسومر
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'group_name',  # نام گروه مورد نظر خود را قرار دهید
        {
            'type': 'send_user_id',
            'user_id': user_id,
        }
    )

    try:
        # in_progress=True:
        # user is still working
        at = AttendanceUser.objects.get(user=request.user, in_progress=True)

        # print("at = AttendanceUser.objects.get(user=request.user, in_progress=True)")
        return render(request, 'Attendance_app/start.html', {'started': at.start, 'pk': at.token, 'at': at})
    except AttendanceUser.DoesNotExist:

        try:
            # If the user starts working twice or more in one day,
            # instead of creating a new record, it will be taken and updated:
            at = AttendanceUser.objects.get(user=request.user, created_date=date)
            if at.confirmation is None:
                if location:
                    return redirect(reverse('Attendance:get_user_location'))

            # for access to the start and end before start working again
            if not str(at.end)[0:8] in at.last_info:
                at.last_info += f" \n start={str(at.start)[0:8]}, end={str(at.end)[0:8]}*"
            print(start)

            at.start = start

            at.in_progress = True
            at.save()
            # print("at = AttendanceUser.objects.get(user=request.user, created_date=date)")
            return render(request, 'Attendance_app/start.html', {'started': start, 'pk': at.token, 'at': at})
        except AttendanceUser.DoesNotExist:

            at = AttendanceUser.objects.create(user=request.user, created_date=date, )
            at.in_progress = True
            at.token = uuid.uuid4()
            at.start = start
            at.save()
            if location:
                return redirect(reverse('Attendance:get_user_location'))

            # print("at = AttendanceUser.objects.create(user=request.user, created_date=date, start=start,)")
            return render(request, 'Attendance_app/start.html', {'started': start, 'pk': at.token, 'at': at})


# def update_duration_view(request):
#     try:
#         attend = get_object_or_404(AttendanceUser, user=request.user, in_progress=True)
#         attend.end = datetime.now().time()
#         # Calculate the duration of working time
#         job_time = datetime.combine(datetime.min, attend.end) - datetime.combine(datetime.min, attend.start)
#         profile = Profile.objects.get(user_id=request.user)
#         # Calculate the number of hours elapsed since the record was created
#         if attend.created_date < datetime.now().date():
#             date_hours = datetime.now().date() - attend.created_date
#             if job_time.days == date_hours.days:
#                 attend.save()
#                 job_time = timedelta(seconds=job_time.total_seconds())
#
#                 inc = round(profile.profile_position.position_income * (attend.job_time.total_seconds() / 3600), 4)
#                 attend.job_time += job_time  # Convert to timedelta object
#
#                 duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
#                 duration_formatted = duration_formatted.replace("day", "روز")  # Replace "day" with "روز"
#                 return JsonResponse({'duration_formatted': duration_formatted, 'inc': inc})
#             else:
#                 # Add 24 hours for each day that has passed
#                 job_time += timedelta(days=date_hours.days)
#                 attend.save()
#                 job_time = timedelta(seconds=job_time.total_seconds())
#                 attend.job_time += job_time  # Convert to timedelta object
#                 inc = round(profile.profile_position.position_income * (attend.job_time.total_seconds() / 3600), 4)
#                 duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
#                 duration_formatted = duration_formatted.replace("day", "روز")  # Replace "day" with "روز"
#                 return JsonResponse({'duration_formatted': duration_formatted, 'inc': inc})
#         else:
#             attend.save()
#             job_time = timedelta(seconds=job_time.total_seconds())
#             attend.job_time += job_time  # Convert to timedelta object
#             inc = round(profile.profile_position.position_income * (attend.job_time.total_seconds() / 3600), 4)
#             duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
#             return JsonResponse({'duration_formatted': duration_formatted, 'inc': inc})
#     except AttendanceUser.DoesNotExist:
#         return JsonResponse({'duration_formatted': '0:00:00'})


@login_required
def process_result_view(request, pk):
    attend = get_object_or_404(AttendanceUser, user=request.user, token=pk)
    # To ensure
    if not attend.in_progress:
        now = timezone.now()
        month = jdatetime.date.fromgregorian(date=now.date()).month
        return redirect(reverse("Attendance:result_list", kwargs={"pk": request.user.id, 'month': month}, ))

    attend.in_progress = False
    attend.end = datetime.now().time()
    # Calculate the duration of working time
    job_time = datetime.combine(datetime.min, attend.end) - datetime.combine(datetime.min, attend.start)
    # Calculate the number of hours elapsed since the record was created
    date_hours = datetime.now().date() - attend.created_date

    # Add 24 hours for each day that has passed
    job_time += timedelta(days=date_hours.days)

    attend.job_time += job_time
    attend.save()
    return redirect(reverse("price:procces_pricing", kwargs={'pk': pk}))


class ShowResult(TemplateView):
    template_name = 'Attendance_app/result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        request = self.request

        try:

            pk = self.kwargs['pk']
            print(1)
            id = self.kwargs['user']
            attend = get_object_or_404(AttendanceUser, user_id=id, id=pk)
        except:
            token = self.request.session['token']

            attend = get_object_or_404(AttendanceUser, user=request.user,
                                       token=token)  # token=pk if there is no session
        now = timezone.now()
        month = jdatetime.date.fromgregorian(date=now.date()).month
        context['month'] = month
        context['object'] = attend
        context['user'] = CustomUser.objects.get(id=request.user.id)

        # get attend.end and start in datetime type
        end_datetime = attend.end
        start_datetime = attend.start
        job_time = str(attend.job_time)
        if 'day' in job_time:
            job_time = job_time.replace("day", "روز")[:14]
        else:
            job_time = job_time[:7]
        # Format the datetime objects
        end1 = end_datetime.strftime("%H:%M:%S %p")
        start2 = start_datetime.strftime("%H:%M:%S %p")

        starts = []
        ends = []

        pattern = r"start=(\d{2}:\d{2}:\d{2}), end=(\d{2}:\d{2}:\d{2})"

        matches = re.findall(pattern, attend.last_info)

        for match in matches:
            start, end = match
            starts.append(start)
            ends.append(end)

        zipped_times = zip(starts, ends)
        at_month = attend.created_date.month

        income = Income.objects.get(USer=attend.user, month=at_month)
        job_time = datetime.combine(datetime.min, attend.end) - datetime.combine(datetime.min, attend.start)
        inc = round(income.position.profile_position.position_income * (job_time.total_seconds() / 3600), 4)
        context['income'] = income
        context['end'] = end1
        context['start'] = start2
        context['job_time'] = job_time
        context['zipped_times'] = zipped_times
        context['inc'] = inc
        context['date'] = attend.created_date
        return context
