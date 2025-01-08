import jdatetime
from django.utils import timezone

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
        if not attendance.end >= end_shift_time:
            non_progress_users.user.add(attendance.user)
    else:
        non_progress_users.user.add(attendance.user)


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