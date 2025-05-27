from datetime import datetime

from django.http import HttpResponseNotAllowed
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from geopy.distance import geodesic

from Attendance_app.models import AttendanceUser
from .models import Location


# Create your views here.


def get_staff_location(request):
    # if not request.user.is_staff:
    #     return HttpResponseNotAllowed(['GET', 'POST'])
    try:
        location = Location.objects.get(created_by=request.user, active=True)
    except:
        location = False
    return render(request, 'Attendance_app/staff_location.html', {'location': location})


def get_user_location(request):
    return render(request, 'Attendance_app/user_location.html')


@csrf_exempt
def process_user_location(request):
    if request.method == 'POST':
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        user = request.user

        location = Location.objects.get(created_by=request.user.created_who, active=True)
        reference_latitude = location.latitude
        reference_longitude = location.longitude

        # callculate the distance
        distance = geodesic((reference_latitude, reference_longitude), (latitude, longitude)).meters

        date = datetime.now().date()
        at = AttendanceUser.objects.get(user=user, created_date=date)
        start = datetime.now().time()
        if distance < 50:
            print("موقعیت در فاصله کمتر از 50 متر است")
            at.confirmation = True
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
        try:
            location = Location.objects.get(created_by=request.user, active=True)
            location.active = False
            location.save()
        except Location.DoesNotExist:
            location = False

        location = Location.objects.create(longitude=longitude, latitude=latitude, created_by=user, active=True)
        # return HttpResponse(f'{latitude},{longitude}')
        return redirect(reverse('Attendance:redirected_view'))
    else:
        return HttpResponseNotAllowed(['POST'])