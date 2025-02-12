from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
import jdatetime
from django.utils.timezone import now

from pricing.models import Profile
from .models import AttendanceUser



def subscription_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated:
            jalali_date = jdatetime.date.fromgregorian(date=now().date())

            # check user can access
            if user.created_who is None and not user.is_superuser:
                messages.error(request, "Access denied.")
                return redirect(reverse('home:home'))

            if user.subscription_Date and user.subscription_Date <= jalali_date:
                user.is_active = False
                user.save()
                messages.error(request, "Your subscription has expired. Please contact support.")
                return redirect(reverse('home:home'))

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        try:
            position = Profile.objects.get(user=request.user)
        except ObjectDoesNotExist:
            raise AttributeError('داده ی پروفایل شما موجود نیست. با مدیر خود تماس بگیرید')

        return view_func(request, *args, **kwargs)

    return _wrapped_view


def check_progress(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        attendance_obj = AttendanceUser.objects.filter(user=request.user, in_progress=True).first()
        if attendance_obj:
            return redirect(reverse('Attendance:start'))
        return view_func(request, *args, **kwargs)

    return _wrapped_view
