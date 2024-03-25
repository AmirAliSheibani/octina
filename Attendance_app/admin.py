from django.contrib import admin
# from django.contrib.auth.models import User
from .models import AttendanceUser
from pricing.models import CustomUser, Income

User = CustomUser
from django.contrib.admin import AdminSite
from django.db.models.signals import pre_delete
from django.dispatch import receiver

@receiver(pre_delete, sender=AttendanceUser)
def pre_delete_callback(sender, instance, **kwargs):
    at = instance
    income = Income.objects.get(month=at.month, user=at.user)
    inc = income.position.profile_position.position_income * (at.job_time.total_seconds() / 3600)
    income.user_income -= inc
    income.save()

class MyAdminSite(AdminSite):
    site_header = 'مدیریت اُکتینا'

admin_site = MyAdminSite(name='myadmin')
# from django import forms
#
# class AttendanceUserForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.created_by and not self.request.user.is_superuser:
#             self.fields['created_by'].queryset = User.objects.filter(id=self.instance.created_by.id)

class AttendanceUserAdmin(admin.ModelAdmin):
    fields = ('user', 'created_date', 'start', 'end', 'job_time', 'token', 'last_info', 'in_progress', 'confirmation')
    list_display = ['user', 'created_date', 'start', 'end', 'job_time', 'in_progress', 'confirmation']

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            if db_field.name == 'user':
                kwargs["queryset"] = User.objects.filter(created_who=request.user)
                return super().formfield_for_foreignkey(db_field, request, **kwargs)
        else:
            return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        # Only show objects created by the current user
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(created_by=request.user)
        return qs


admin.site.register(AttendanceUser, AttendanceUserAdmin)

