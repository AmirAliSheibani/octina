from datetime import datetime

import jdatetime
from django.db.models import Q
from django.utils import timezone

from Attendance_app.models import AttendanceUser
from pricing.models import Profile, NoneInProgress


def get_jalali_date():
    """
    Returns the current Jalali month and year.
    """
    current_date = now = timezone.now()
    jalali_date = jdatetime.date.fromgregorian(date=current_date)
    return jalali_date.month, jalali_date.year


def get_jalali_date():
    now = timezone.now()
    jalali_date = jdatetime.date.fromgregorian(date=now.date())
    return jalali_date.month, jalali_date.year


def get_day_mapping():
    return {
        5: 0,  # Saturday
        6: 1,  # Sunday
        0: 2,  # Monday
        1: 3,  # Tuesday
        2: 4,  # Wednesday
        3: 5,  # Thursday
        4: 6,  # Friday
    }


def get_current_shift(shiftwork, reversed_day_number):
    return shiftwork.filter(work_days__day_of_week=reversed_day_number).last()


def handle_non_progress_users(attendance, current_shift, end_shift_time, non_progress_users):
    if current_shift:
        if not attendance.end >= end_shift_time or attendance.job_time >= current_shift.required_time:
            non_progress_users.user.add(attendance.user)
            attendance.user.absent = True
    else:
        non_progress_users.user.add(attendance.user)
        attendance.user.absent = True

def get_month_names():
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
    return MONTH_NAMES


def handle_progress_and_none_progress_user(users):
    """
    Handles in-progress and non-progress users based on attendance data.

    Args:
        users (QuerySet): QuerySet of CustomUser objects.

    Returns:
        dict: A dictionary containing:
              - 'in_progress_users': List of users currently in progress.
              - 'non_progress_users': NoneInProgress object for absent users.
              - 'not_accepted_vacation': QuerySet of vacations not accepted by employer.
              - 'attendance_obj': QuerySet of AttendanceUser with incomplete confirmations.
              - 'filter_non_progress': Filtered NoneInProgress objects for the current month.
    """
    now = timezone.now()
    month, year = get_jalali_date()
    day_mapping = get_day_mapping()

    # Users with incomplete confirmations or absences
    attendance_obj = AttendanceUser.objects.filter(
        Q(user__in=users) & (Q(confirmation=False) | Q(confirmation=None))
    )

    attendance_users = AttendanceUser.objects.filter(user__in=users)

    # Users currently working and absent users
    in_progress_users = []
    non_progress_users, _ = NoneInProgress.objects.get_or_create(
        created_date=jdatetime.date.fromgregorian(date=now.date())
    )

    # Process user attendance
    for attendance in attendance_users:
        profile = Profile.objects.filter(user=attendance.user).last()
        if not profile:
            continue

        # Check if user works full at the shift time
        shiftwork = profile.profile_position.shift_work
        current_day_number = now.weekday()
        reversed_day_number = day_mapping[current_day_number]
        current_shift = get_current_shift(shiftwork, reversed_day_number)

        if attendance.in_progress:
            in_progress_users.append(attendance.user)
            attendance.user.absent = False

            if attendance.user in non_progress_users.user.all():
                non_progress_users.user.remove(attendance.user)
        else:
            end_shift_time = current_shift.work_end_time if current_shift else None
            handle_non_progress_users(attendance, current_shift, end_shift_time, non_progress_users)
        attendance.user.save()

    # Add absent users
    non_progress_users.user.add(
        *users.exclude(username__in=in_progress_users)
        .exclude(id__in=non_progress_users.user.values_list('id', flat=True))
    )

    return {
        'in_progress_users': in_progress_users,
        'non_progress_users': non_progress_users,
        'attendance_obj': attendance_obj,
    }
