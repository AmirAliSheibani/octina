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
    paginate_by = 30

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        context["object"] = AttendanceUser.objects.filter(user_id=pk)
        context['user'] = CustomUser.objects.get(id=pk)
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
def staff_user_list(request, pk):
    if not request.user.is_superuser:
        users = CustomUser.objects.filter(created_who=request.user)
        positions = Profile.objects.filter(created_by=request.user)
        attendances = AttendanceUser.objects.filter(user__in=users)
        income = Income.objects.filter(USer__in=users)
        return render(request, 'Attendance_app/AdminUserLlist.html',
                      {'object': zip(users, positions, attendances, income)})

    users = CustomUser.objects.all()
    positions = Profile.objects.all()
    attendances = AttendanceUser.objects.filter(user__in=users)
    income = Income.objects.filter(USer__in=users)
    return render(request, 'Attendance_app/AdminUserLlist.html', {'object': zip(users, positions, attendances, income)})


import re


@login_required
def result_detail(request, pk):
    result = AttendanceUser.objects.get(id=pk)
    starts = []
    ends = []

    pattern = r"start=(\d{2}:\d{2}), end=(\d{2}:\d{2})"
    matches = re.findall(pattern, result.last_info)

    for match in matches:
        start, end = match
        starts.append(start)
        ends.append(end)

    zipped_times = zip(starts, ends)

    return render(request, 'Attendance_app/result.html', {'zipped_times': zipped_times})


@login_required
def create_attendance_view(request):
    position = Profile.objects.get(user=request.user)
    return render(request, 'Attendance_app/index.html', {'position': position})


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
            if not str(at.end)[0:5] in at.last_info:
                at.last_info += f" \n start={str(at.start)[0:5]}, end={str(at.end)[0:5]}*"
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
        return redirect("Attendance:result_list")

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
            id = self.kwargs['user']
            attend = get_object_or_404(AttendanceUser, user_id=id,
                                       token=token)  # token=pk if there is no session

        context['object'] = attend
        context['user'] = CustomUser.objects.get(id=id)

        # get attend.end and start in datetime type
        end_datetime = attend.end
        start_datetime = attend.start
        job_time = str(attend.job_time)

        # Format the datetime objects
        end = end_datetime.strftime("%H:%M:%S %p")
        start = start_datetime.strftime("%H:%M:%S %p")

        starts = []
        ends = []

        pattern = r"start=(\d{2}:\d{2}), end=(\d{2}:\d{2})"
        matches = re.findall(pattern, attend.last_info)

        for match in matches:
            start, end = match
            starts.append(start)
            ends.append(end)

        zipped_times = zip(starts, ends)

        context['end'] = end
        context['start'] = start
        context['job_time'] = job_time
        context['zipped_times'] = zipped_times
        return context
