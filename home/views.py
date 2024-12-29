from django.shortcuts import render, redirect
from . import models
from django.core.mail import send_mail

def home(request):
    context = {}
    slider = models.Slider.objects.all()
    services = models.Service.objects.all()
    about = models.About.objects.all()
    whyUS = models.WhyUs.objects.all()
    team = models.Team.objects.all()

    context['slider'] = slider
    context['services'] = services
    context['about'] = about
    context['whyUS'] = whyUS
    context['team'] = team
    return render(request, 'home/index.html')

def slidermore(request,pk):
    context = {}

    slider = models.Slider.objects.get(id=pk)

    context['object'] = slider

    return render(request, 'home/readmore.html', context)


def about(request):

    context = {}
    about = models.About.objects.all()
    context['about'] = about
    return render(request, 'home/about.html', context)


def service(request):
    context = {}
    services = models.Service.objects.all()
    context['services'] = services
    return render(request, 'home/service.html', context)


def team(request):
    context = {}
    team = models.Team.objects.all()
    context['team'] = team
    return render(request, 'home/team.html', context)


def why(request):
    context = {}
    whyUS = models.WhyUs.objects.all()
    context['whyUS'] = whyUS
    return render(request, 'home/why.html', context)

