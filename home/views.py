from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from django.views.generic import TemplateView
from . import models

class BaseModelView(TemplateView):
    """Base view to fetch model data for the context."""

    model = None  # The model to fetch data from
    context_name = None  # The key to use in the context

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model and self.context_name:
            context[self.context_name] = self.model.objects.all()
        return context


class HomeView(TemplateView):
    template_name = 'home/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slider'] = models.Slider.objects.all()
        context['services'] = models.Service.objects.all()
        context['about'] = models.About.objects.all()
        context['whyUS'] = models.WhyUs.objects.all()
        context['team'] = models.Team.objects.all()
        return context


class SliderMoreView(BaseModelView):
    template_name = 'home/readmore.html'
    model = models.Slider
    context_name = 'slider'


class AboutView(BaseModelView):
    template_name = 'home/about.html'
    model = models.About
    context_name = 'about'


class ServiceView(BaseModelView):
    template_name = 'home/service.html'
    model = models.Service
    context_name = 'services'


class TeamView(BaseModelView):
    template_name = 'home/team.html'
    model = models.Team
    context_name = 'team'


class WhyUsView(BaseModelView):
    template_name = 'home/why.html'
    model = models.WhyUs
    context_name = 'whyUS'


