from django import template

"""
Custom django template filters
"""

register = template.Library()


@register.filter()
def lookup(d, key):
    """
    template filter to lookup an array entry
    :param d: array
    :param key: entry key
    :return: value of the array entry
    """
    return d[key]


@register.filter
def get_attr(obj, attr_name):
    """
    template filter to lookup an object attribute
    :param obj: object to be looked inside
    :param attr_name: attribute to be looked up in the attribute
    :return:
    """
    return getattr(obj, attr_name, None)
