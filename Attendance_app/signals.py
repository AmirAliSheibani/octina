from Attendance_app.models import AttendanceUser
from pricing.models import recalculate_income

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=AttendanceUser)
def set_month_year(sender, instance, created, **kwargs):
    if created and instance.created_date:
        instance.month = instance.created_date.month
        instance.year = instance.created_date.year
        instance.save()

@receiver(post_save, sender=AttendanceUser)
def update_income_on_save(sender, instance, **kwargs):
    print(instance.user, instance.month, instance.year)
    recalculate_income(instance.user, instance.month, instance.year)


@receiver(post_delete, sender=AttendanceUser)
def update_income_on_delete(sender, instance, **kwargs):
    print(instance.user, instance.month, instance.year)
    recalculate_income(instance.user, instance.month, instance.year)