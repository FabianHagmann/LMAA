from django import template

register = template.Library()


@register.filter()
def lookup(d, key):
    return d[key]


@register.filter
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, None)
