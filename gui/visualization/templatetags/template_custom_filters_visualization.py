from django import template

from gui.assignments.models import Solution

"""
Custom django template filters
"""


register = template.Library()


@register.filter()
def format_timestamp(timestamp):
    """
    formats a timestamp to the format YYYY-mm-dd HH:MM:SS
    :param timestamp: timestamp to be formatted
    :return: formatted timestamp as a string
    """

    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


@register.filter()
def to_float(string):
    """
    converts a string into a float valuer. May only be called with valid inputs
    :param string: string to be converted
    :return: converted float
    """

    return float(string)


@register.filter()
def has_solutions(assignment_id):
    """
    checks if any solutions exist for the given assignment
    :param assignment_id: assignment to be checked
    :return: true if solutions exist, otherwise false
    """

    return Solution.objects.filter(assignment_id=assignment_id).exists()
