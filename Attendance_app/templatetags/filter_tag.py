from django import template

register = template.Library()

def cutter(value, arg):
    return value[:arg]
register.filter("cutter", cutter)



@register.filter
def zip(list1, list2):
    return zip(list1, list2)