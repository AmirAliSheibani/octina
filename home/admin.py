from django.contrib import admin
from . import models


@admin.register(models.Slider)
class AdminSlider(admin.ModelAdmin):
    list_display = ['title']


@admin.register(models.Service)
class AdminService(admin.ModelAdmin):
    list_display = ['title']


@admin.register(models.About)
class AdminAbout(admin.ModelAdmin):
    list_display = ['title']


@admin.register(models.WhyUs)
class AdminWhy(admin.ModelAdmin):
    list_display = ['title']


@admin.register(models.Team)
class AdminTeam(admin.ModelAdmin):
    list_display = ['name', 'position']
