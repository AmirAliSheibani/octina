from django import template
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils import translation

register = template.Library()

def cutter(value, arg):
    return value[:arg]

register.filter("cutter", cutter)


@register.filter
def zip_lists(list1, list2):
    return zip(list1, list2)


@register.filter
def is_selected(day, shift):
    return day in shift.work_days.all()


@register.filter
def formatted_price(price):
    with translation.override('en'):
        return intcomma(int(price)) if price else None

