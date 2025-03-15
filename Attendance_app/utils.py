from datetime import datetime
from django.db.models import Case, When, Value, BooleanField
import jdatetime
from django.db.models import Q
from django.http import Http404
from django.utils import timezone
import re
from Attendance_app.models import AttendanceUser
from pricing.models import Profile, NoneInProgress, CustomUser


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
    """ Handles in-progress and non-progress users based on attendance data. """

    now = timezone.now()

    # Optimized queryset fetching
    attendance_users = AttendanceUser.objects.filter(user__in=users).select_related(
        "user__profile", "user__profile__profile_position"
    ).prefetch_related("user__noneinprogress_set")

    # Users with incomplete confirmations or absences
    attendance_obj = AttendanceUser.objects.filter(
        Q(user__in=users) & (Q(confirmation=False) | Q(confirmation=None))
    )

    # Get or create NoneInProgress object for absent users
    non_progress_users, _ = NoneInProgress.objects.get_or_create(
        created_date=jdatetime.date.fromgregorian(date=now.date())
    )

    # Get in-progress users
    in_progress_users = attendance_users.filter(in_progress=True).values_list("user", flat=True)

    # Bulk update absent status


    # دریافت کاربران در حال کار
    in_progress_users_ids = list(AttendanceUser.objects.filter(in_progress=True).values_list("user_id", flat=True))


    # آپدیت کاربران به‌صورت مستقیم
    CustomUser.objects.update(
        absent=Case(
            When(id__in=in_progress_users_ids, then=Value(False)),
            default=Value(True),
            output_field=BooleanField(),
        )
    )

    # Add absent users to NoneInProgress
    absent_users = users.exclude(id__in=in_progress_users).exclude(
        id__in=non_progress_users.user.values_list('id', flat=True))
    non_progress_users.user.add(*absent_users)
    # دریافت لیست ID کاربران
    # دریافت فقط کاربران (User objects)
    staff_none_progress_users = users.filter(absent=True)

    # تعداد کاربران
    staff_none_progress_count = staff_none_progress_users.count()
    return {
        'in_progress_users': list(in_progress_users),
        'non_progress_users': non_progress_users,
        'staff_none_progress_users': staff_none_progress_count,
        'attendance_obj': attendance_obj,
    }

def extract_time_ranges(attendance_info):
    """Extract start and end times from last_info field."""
    pattern = r"start=(\d{2}:\d{2}:\d{2}), end=(\d{2}:\d{2}:\d{2})"
    return zip(*re.findall(pattern, attendance_info))


def has_access(request, user):
    req_user = request.user
    if user != req_user and not (req_user.is_staff and user.created_who == req_user):
        raise Http404("شما اجازه دسترسی به این اطلاعات را ندارید.")
    return True