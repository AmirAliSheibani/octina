import math
import uuid
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.urls import reverse
from datetime import datetime, timedelta
from django.views.generic import TemplateView
from django.views.generic.list import ListView
from .models import AttendanceUser
from .mixin import CustomizedRquirementLogin
from django.contrib.auth.decorators import login_required
from pricing.models import Profile, User, CustomUser, Income
from .form import PositionForm
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
# exel

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from django.http import HttpResponse
from django.db.models import Q

@login_required
def restricted_view(request):
    user = request.user

    # Check if the subscription date is today
    if user.subscription_Date and user.subscription_Date <= timezone.now().date():
        # Disable the user or perform any other desired action
        user.is_active = False
        user.save()

        # Redirect or display an appropriate message to the user
        return HttpResponse("Your subscription has expired. Please contact support.")
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
            att = AttendanceUser.objects.filter(user_id=pk, created_date__month=month)
            context['user'] = CustomUser.objects.get(id=pk)
            at = att.last()
            at_month = at.created_date.month
            try:
                income = Income.objects.get(USer=at.user, created_date__month=at_month)

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
                results.append(str(result)[:6])

            # Pass the objects and results to the template context

            context["object"] = zip(att, results)
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
    attendances = AttendanceUser.objects.filter(user=user, created_date__month=month)
    income = Income.objects.get(USer=user, created_date__month=month)
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


    # Write table data
    row_num = 3
    for attendance in attendances:
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        sheet[f"C{row_num}"] = positions.profile_position.positions  # Extract the position attribute
        sheet[f"D{row_num}"] = str(attendance.job_time)[:10]
        inc = income.position.profile_position.position_income * (attendance.job_time.total_seconds() / 3600)
        sheet[f"E{row_num}"] = inc
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
        positions = Profile.objects.filter(created_by=request.user)
        attendances = AttendanceUser.objects.filter(user__in=users, created_date__month=month)
        income = Income.objects.filter(USer__in=users, created_date__month=month)

    else:
        users = CustomUser.objects.all()
        positions = Profile.objects.all()
        attendances = AttendanceUser.objects.filter(user__in=users, created_date__month=month)
        income = Income.objects.filter(USer__in=users, created_date__month=month)

    no_income_users = users.exclude(id__in=income.values_list('USer_id', flat=True))


    # Filter by last name alphabets
    last_name_filter = request.GET.get('last_name_filter')
    if last_name_filter:
        users = users.filter(last_name__startswith=last_name_filter)

    # Filter by job time
    job_time_filter = request.GET.get('job_time_filter')
    if job_time_filter:
        if job_time_filter == 'smaller':
            income = income.order_by('job_time')
        elif job_time_filter == 'greater':
            income = income.order_by('-job_time')

    # Filter by income
    income_filter = request.GET.get('income_filter')
    if income_filter:
        if income_filter == 'smaller':
            income = income.order_by('User_income')
        elif income_filter == 'greater':
            income = income.order_by('-User_income')

    return render(request, 'Attendance_app/AdminUserLlist.html',
                  {'object': zip(users, positions, attendances, income),'checkincome':no_income_users, 'noIncome': zip(no_income_users, positions),
                   'months': MONTH_NAMES, 'month': month})


@login_required
def download_excel(request, pk, month):
    if not request.user.is_superuser:
        users = CustomUser.objects.filter(created_who=request.user)
        positions = Profile.objects.filter(created_by=request.user)
        attendances = AttendanceUser.objects.filter(user__in=users, created_date__month=month)
        income = Income.objects.filter(USer__in=users, created_date__month=month)
    else:
        users = CustomUser.objects.all()
        positions = Profile.objects.all()
        attendances = AttendanceUser.objects.filter(user__in=users, created_date__month=month)
        income = Income.objects.filter(USer__in=users, created_date__month=month)

    no_income_users = users.exclude(id__in=income.values_list('USer_id', flat=True))

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

    # Write table data
    row_num = 3
    for user, position, attendance, user_income in zip(users, positions, attendances, income):
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        sheet[f"C{row_num}"] = position.profile_position.positions  # Extract the position attribute
        sheet[f"D{row_num}"] = str(attendance.job_time)[:10]
        sheet[f"E{row_num}"] = user_income.User_income
        row_num += 1

    # Apply styles
    red_fill = PatternFill(start_color="FF0000", end_color="FF0000", fill_type="solid")
    for user, position in zip(no_income_users, positions ):
        sheet[f"A{row_num}"] = user.username
        sheet[f"B{row_num}"] = user.last_name
        sheet[f"C{row_num}"] = position.profile_position.positions
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
        income = Income.objects.get(USer=at.user, created_date__month=at_month)
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


@login_required
def create_attendance_view(request):
    position = Profile.objects.get(user=request.user)
    month = timezone.now().month
    print(month)
    try:
        income = Income.objects.get(USer=request.user, created_date__month=month).User_income
        print(income)
        print(1)
    except:
        income = 'خالی'
        print(1)

    return render(request, 'Attendance_app/index.html', {'position': position, 'income': income, 'month': month})


@login_required
def start_attendance_view(request):
    start = datetime.now().time()
    date = datetime.now().date()
    try:
        # in_progress=True:
        # user is still working
        at = AttendanceUser.objects.get(user=request.user, in_progress=True)

        # print("at = AttendanceUser.objects.get(user=request.user, in_progress=True)")
        return render(request, 'Attendance_app/start.html', {'started': at.start, 'pk': at.token})
    except AttendanceUser.DoesNotExist:
        try:
            # If the user starts working twice or more in one day,
            # instead of creating a new record, it will be taken and updated:
            at = AttendanceUser.objects.get(user=request.user, created_date=date)
            # for access to the start and end before start working again
            if not str(at.end)[0:8] in at.last_info:
                at.last_info += f" \n start={str(at.start)[0:8]}, end={str(at.end)[0:8]}*"
            print(start)

            at.start = start

            at.in_progress = True
            at.save()
            # print("at = AttendanceUser.objects.get(user=request.user, created_date=date)")
            return render(request, 'Attendance_app/start.html', {'started': start, 'pk': at.token})
        except AttendanceUser.DoesNotExist:

            at = AttendanceUser.objects.create(user=request.user, created_date=date, start=start, )
            at.in_progress = True
            at.token = uuid.uuid4()
            at.save()
            # print("at = AttendanceUser.objects.create(user=request.user, created_date=date, start=start,)")
            return render(request, 'Attendance_app/start.html', {'started': start, 'pk': at.token})


def update_duration_view(request):
    try:
        attend = get_object_or_404(AttendanceUser, user=request.user, in_progress=True)
        attend.end = datetime.now().time()
        # Calculate the duration of working time
        job_time = datetime.combine(datetime.min, attend.end) - datetime.combine(datetime.min, attend.start)
        # Calculate the number of hours elapsed since the record was created
        if attend.created_date < datetime.now().date():
            date_hours = datetime.now().date() - attend.created_date
            if job_time.days == date_hours.days:
                attend.save()
                job_time = timedelta(seconds=job_time.total_seconds())

                attend.job_time += job_time  # Convert to timedelta object
                duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
                return JsonResponse({'duration_formatted': duration_formatted})
            else:
                # Add 24 hours for each day that has passed
                job_time += timedelta(days=date_hours.days)
                attend.save()
                job_time = timedelta(seconds=job_time.total_seconds())
                attend.job_time += job_time  # Convert to timedelta object

                duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
                return JsonResponse({'duration_formatted': duration_formatted})
        else:
            attend.save()
            job_time = timedelta(seconds=job_time.total_seconds())
            attend.job_time += job_time  # Convert to timedelta object

            duration_formatted = str(attend.job_time).split(".")[0]  # Extract the hours:minutes:seconds part
            return JsonResponse({'duration_formatted': duration_formatted})
    except AttendanceUser.DoesNotExist:
        return JsonResponse({'duration_formatted': '0:00:00'})


@login_required
def process_result_view(request, pk):
    attend = get_object_or_404(AttendanceUser, user=request.user, token=pk)
    # To ensure
    if not attend.in_progress:
        return redirect(reverse("Attendance:result_list", kwargs={"pk": request.user.id}))

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
        month = timezone.now().month
        context['month'] = month
        context['object'] = attend
        context['user'] = CustomUser.objects.get(id=request.user.id)

        # get attend.end and start in datetime type
        end_datetime = attend.end
        start_datetime = attend.start
        job_time = str(attend.job_time)

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
        income = Income.objects.get(USer=attend.user, created_date__month=at_month)

        context['income'] = income
        context['end'] = end1
        context['start'] = start2
        context['job_time'] = job_time
        context['zipped_times'] = zipped_times
        return context
