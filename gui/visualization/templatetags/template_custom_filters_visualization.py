from django import template

register = template.Library()


@register.filter()
def format_timestamp(timestamp):
    return type(timestamp)
