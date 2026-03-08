from django import template

register = template.Library()

@register.filter
def divideby(value, arg):
    try:
        return int(value) // int(arg)
    except (ValueError, ZeroDivisionError):
        return None

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError):
        return None
