import jdatetime
from django.utils import timezone

def get_jalali_date():
    """
    Returns the current Jalali month and year.
    """
    current_date = now = timezone.now()
    jalali_date = jdatetime.date.fromgregorian(date=current_date)
    return jalali_date.month, jalali_date.year