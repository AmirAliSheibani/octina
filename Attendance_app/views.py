import uuid
from locations.models import Location
import re
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
from jalali_date import datetime2jalali

from .forms import StaffCreateUser, ShiftWorkForm, PositionForm, ProfileForm, HolidayForm, VacationForm, \
    UpdateProfileForm
from .models import AttendanceUser
from .mixin import CustomizedRquirementLogin
from django.contrib.auth.decorators import login_required, user_passes_test
from pricing.models import Profile, User, CustomUser, Income, ShiftWork, Positions, Holidays, Vacation, \
    VacationType, Day, NoneInProgress
from django.http import JsonResponse, HttpResponse, HttpResponseNotAllowed
from django.utils import timezone
# exel

import openpyxl
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from .utils import get_jalali_date, get_day_mapping, get_current_shift, handle_non_progress_users, get_month_names, \
    handle_progress_and_none_progress_user
from django.http import HttpResponse
from django.db.models import Q

from .decorators import check_progress, profile_required, subscription_required
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import F


@subscription_required
@profile_required
def restricted_view(request, *args, **kwargs):
    return redirect('Attendance:home')


# homepage
@login_required
@check_progress
def create_attendance_view(request):
    position = Profile.objects.get(user=request.user)
    now = timezone.now()
    month, year = get_jalali_date()

    # Calculate user's income
    try:
        income_obj = Income.objects.get(month=month, year=year, user=request.user)
        income = income_obj.user_income
    except Income.DoesNotExist:
        income = None

    # If the user is a staff member
    if request.user.is_staff:
        location = Location.objects.filter(created_by=request.user).exists()

        # Users associated with the manager
        users = CustomUser.objects.filter(created_who=request.user)
        progress_data = handle_progress_and_none_progress_user(users)

        not_accepted_vacation = Profile.objects.filter(user__in=users, vacation__check_by_employer=False)
        none_progress_count = CustomUser.objects.filter(created_who=request.user, absent=True)
        no_confirmation = AttendanceUser.objects.filter(
            user__in=users,
            confirmation__in=[False, None]
        )
        for c in not_accepted_vacation:
            print(c)
        # Filter absent users for the current month
        filter_non_progress = NoneInProgress.objects.filter(month=month, user__in=users).exclude(
            created_date=jdatetime.date.fromgregorian(date=now.date())
        )

        return render(request, 'Attendance_app/index.html', {
            'position': position,
            'income': income,
            'month': month,
            'year': year,
            'no_confirmation_users': no_confirmation,
            'in_progress_users': progress_data['in_progress_users'],
            'none_progression_count': none_progress_count.count(),
            'users': users,
            'location': location,
            'not_accepted_vacation': not_accepted_vacation,
            'filter_non_progress': filter_non_progress,
        })

    return render(request, 'Attendance_app/index.html', {
        'position': position,
        'income': income,
        'year': year,
        'month': month,
    })


class AttendanceListView(CustomizedRquirementLogin, ListView):
    model = AttendanceUser

    def get_income_or_create(self, attendance_obj):
        """
        Retrieve or create an Income object for the given attendance object.
        """
        try:
            return Income.objects.get(
                month=attendance_obj.created_date.month,
                year=attendance_obj.created_date.year,
                user=attendance_obj.user
            )
        except Income.DoesNotExist:
            profile = Profile.objects.get(user=attendance_obj.user)
            job_time_hours = attendance_obj.job_time.total_seconds() / 3600
            income = Income.objects.create(
                created_date=attendance_obj.created_date,
                user=attendance_obj.user,
                position=profile,
                job_time=attendance_obj.job_time,
                user_income=profile.position_income * job_time_hours,
                created_by=self.request.user.created_who
            )
            income.save()
            return income

    def format_job_time(self, job_time_str):
        """
        Format the job time string into a localized format.
        """
        if 'day' in job_time_str:
            return job_time_str.replace("day", "روز")[:14]
        return job_time_str[:7]

    def calculate_income(self, attendance, position_income):
        """
        Calculate the income for a specific attendance entry.
        """
        return round(position_income * (attendance.job_time.total_seconds() / 3600), 4)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        month = self.kwargs['month']
        year = self.kwargs['year']
        context['months'] = get_month_names()

        try:
            user = CustomUser.objects.get(id=pk)
            attendances = AttendanceUser.objects.filter(month=month, year=year, user_id=pk)
            context['user'] = user

            if not attendances.exists():
                raise AttendanceUser.DoesNotExist("No attendance records found for the given user and date range.")

            attendance_obj = attendances.first()
            income = self.get_income_or_create(attendance_obj)

            position_income = income.position.profile_position.position_income
            job_time_list = []
            results = []

            for attendance in attendances:
                results.append(self.calculate_income(attendance, position_income))
                job_time_list.append(self.format_job_time(str(attendance.job_time)))

            context["object"] = zip(attendances, results, job_time_list)
            context['income'] = income

        except AttendanceUser.DoesNotExist:
            context["object"] = None
            context['user'] = CustomUser.objects.get(id=pk)
            context['income'] = None

        context['month'] = month
        context['year'] = year
        return context




@login_required
def result_detail(request, pk):
    attendance_obj = AttendanceUser.objects.get(id=pk)
    at_month = attendance_obj.created_date.month
    at_year = attendance_obj.created_date.year
    starts = []
    ends = []
    try:
        income = Income.objects.get(
            month=at_month,
            yar=at_year,
            user=attendance_obj.user
        )
    except:
        income = Income.objects.create(created_date=attendance_obj.created_date, user=attendance_obj.user,
                                       position=Profile.objects.get(user=attendance_obj.user), job_time=attendance_obj.job_time)
        income.user_income = income.position.profile_position.position_income * (
                income.job_time.total_seconds() / 3600)
        print(request.user.is_staff)
        income.created_by = request.user.created_who
        income.save()

    pattern = r"start=(\d{2}:\d{2}:\d{2}), end=(\d{2}:\d{2}:\d{2})"
    matches = re.findall(pattern, attendance_obj.last_info)

    for match in matches:
        start, end = match
        starts.append(start)
        ends.append(end)

    zipped_times = zip(starts, ends)

    return render(request, 'Attendance_app/result.html', {'zipped_times': zipped_times, 'income': income})

@login_required
def start_attendance_view(request):
    day_mapping = get_day_mapping()
    current_day_number = datetime.now().weekday()
    reversed_day_number = day_mapping[current_day_number]
    current_hafte = {
        0: 'شنبه',
        1: 'یک شنبه',
        2: 'دو شنبه ',
        3: 'سه شنبه',
        4: 'چهار شنبه',
        5: 'پنج شنبه',
        6: 'جمعه',
    }
    current_day = current_hafte[reversed_day_number]
    try:
        location = Location.objects.get(created_by=request.user.created_who, active=True)
        print('location = True')
    except Location.DoesNotExist:
        location = False
        print('location = False') #todo make it in one line

    print(current_day)
    start = datetime.now().time()
    date = datetime.now().date()
    work_holi_day = False
    # confirmation = False
    user_id = request.user.id
    profile = Profile.objects.get(user=request.user)
    shiftwork = profile.profile_position.shift_work

    # Get the current day of the week (0 for Monday, 1 for Tuesday, and so on)
    day_mapping = get_day_mapping()

    current_day_number = datetime.now().weekday()
    reversed_day_number = day_mapping[current_day_number]
    print(current_day_number, reversed_day_number)
    check_holidays = datetime.now().date()
    print(check_holidays)
    try:
        # holiday = Holidays.objects.get(date=check_holidays)
        check_holidays = True
    except Holidays.DoesNotExist:
        # holiday = None
        check_holidays = False

    print(check_holidays)

    # Get the corresponding ShiftWork object for the current day
    current_shift = shiftwork.filter(work_days__day_of_week=reversed_day_number).last()

    if current_shift is not None and check_holidays == False:
        start_shift_time = current_shift.work_start_time
        end_shift_time = current_shift.work_end_time

        if not start_shift_time < datetime.now().time() < end_shift_time:
            overtime = True
        else:
            overtime = False
    else:
        work_holi_day = True
        overtime = False  # in fact this is true but for ensure

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
        attendance_obj = AttendanceUser.objects.get(user=request.user, in_progress=True)
        if check_holidays:
            attendance_obj.holiday_check = True
            attendance_obj.save()
        if overtime or work_holi_day:
            attendance_obj.overtime_check = True
            attendance_obj.save()

        # print("attendance_obj = AttendanceUser.objects.get(user=request.user, in_progress=True)")
        return render(request, 'Attendance_app/start.html',
                      {'started': attendance_obj.start, 'pk': attendance_obj.token, 'at': attendance_obj, 'work_in_holi': work_holi_day,
                       'current_day': current_day})
    except AttendanceUser.DoesNotExist:

        try:
            # If the user starts working twice or more in one day,
            # instead of creating a new record, it will be taken and updated:
            attendance_obj = AttendanceUser.objects.get(user=request.user, created_date=date)
            if attendance_obj.confirmation is None:
                if location:
                    return redirect(reverse('Attendance:get_user_location'))

            # for access to the start and end before start working again
            if not str(attendance_obj.end)[0:8] in attendance_obj.last_info:
                attendance_obj.last_info += f" \n start={str(attendance_obj.start)[0:8]}, end={str(attendance_obj.end)[0:8]}*"
            print(start)

            attendance_obj.start = start

            attendance_obj.in_progress = True
            if check_holidays:
                attendance_obj.holiday_check = True

            if overtime or work_holi_day:
                attendance_obj.overtime_check = True

            attendance_obj.save()
            # print("attendance_obj = AttendanceUser.objects.get(user=request.user, created_date=date)")
            return render(request, 'Attendance_app/start.html',
                          {'started': start, 'pk': attendance_obj.token, 'at': attendance_obj, 'work_in_holi': work_holi_day,
                           'current_day': current_day})
        except AttendanceUser.DoesNotExist:

            attendance_obj = AttendanceUser.objects.create(user=request.user, created_date=date)
            attendance_obj.in_progress = True
            attendance_obj.token = uuid.uuid4()
            attendance_obj.start = start
            if check_holidays:
                attendance_obj.holiday_check = True

            if overtime or work_holi_day:
                attendance_obj.overtime_check = True

            attendance_obj.save()
            if location:
                return redirect(reverse('locations:get_user_location'))

            # print("attendance_obj = AttendanceUser.objects.create(user=request.user, created_date=date, start=start,)")
            return render(request, 'Attendance_app/start.html',
                          {'started': start, 'pk': attendance_obj.token, 'at': attendance_obj, 'work_in_holi': work_holi_day,
                           'current_day': current_day})


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
        month, year = get_jalali_date()
        return redirect(
            reverse("Attendance:result_list", kwargs={"pk": request.user.id, 'month': month, 'year': year}, ))

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
            id = self.kwargs['user']
            attend = get_object_or_404(AttendanceUser, user_id=id, id=pk)
        except:
            token = self.request.session['token']

            attend = get_object_or_404(AttendanceUser, user=request.user,
                                       token=token)  # token=pk if there is no session

        month, year = get_jalali_date()
        context['month'] = month
        context['year'] = year
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

        income = Income.objects.get(
            month=at_month,
            year=attend.created_date.year,
            user=attend.user
        )

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


def list_holidays(request):
    staff = request.user
    if not staff.is_staff:
        holidays = Holidays.objects.filter(created_by=staff.created_who)
    else:
        holidays = Holidays.objects.filter(created_by=staff)

    return render(request, 'Attendance_app/holiday_list.html', {'holidays': holidays})


@login_required
def download_excel_user(request, pk, month, year):
    user = CustomUser.objects.get(id=pk)
    positions = Profile.objects.get(user=user)
    attendances = AttendanceUser.objects.filter(
        month=month,
        year=year,
        user=user
    )
    income = Income.objects.get(
        month=month,
        year=year,
        user=user
    )
    MONTH_NAMES = get_month_names()

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
        sheet[f"F{row_num}"] = income.user_income
        row_num += 1

    # Set response content type
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    # Provide a filename for the Excel file
    response["Content-Disposition"] = f"attachment; filename={user.username}_info.xlsx"

    # Save the workbook to the response
    workbook.save(response)
    return response


def getting_vacation(request):
    user = request.user
    if request.method == 'POST':
        form = VacationForm(data=request.POST)
        if form.is_valid():
            vacation = form.save(commit=False)
            vacation.user = request.user
            vacation.save()
            userprofile = Profile.objects.get(user=user)
            userprofile.vacation.add(vacation)
            if userprofile.vacation.count() >= 30:
                raise AttendanceUser('تعداد مرخصی های شما بیش از حد مجاز میباشد')
            userprofile.save()

            form.save_m2m()
            return redirect(reverse('Attendance:redirected_view'))
    else:
        form = VacationForm()
    return render(request, 'Attendance_app/get_vacation.html', {'form': form})


def personal_info(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    position = profile.profile_position
    income = Income.objects.filter(user=user).last()
    return render(request, 'Attendance_app/personal_info.html',
                  {'profile': profile, 'position': position, 'income': income})

