from Attendance_app.models import AttendanceUser
from pricing.models import recalculate_income

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=AttendanceUser)
def update_income_on_save(sender, instance, **kwargs):
    recalculate_income(instance.user, instance.month, instance.year)


@receiver(post_delete, sender=AttendanceUser)
def update_income_on_delete(sender, instance, **kwargs):
    recalculate_income(instance.user, instance.month, instance.year)