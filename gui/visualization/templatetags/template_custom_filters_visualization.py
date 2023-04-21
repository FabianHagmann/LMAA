from django import template

from gui.assignments.models import Solution

register = template.Library()


@register.filter()
def format_timestamp(timestamp):
    return type(timestamp)


@register.filter()
def access_matrix(matrix, indexes):
    if indexes is None:
        return False
    # arg_list = [arg.strip() for arg in indexes.split(',')]
    return matrix[int(indexes)][int(indexes)]


@register.filter()
def to_float(string):
    return float(string)


@register.filter()
def has_solutions(assignment_id):
    return Solution.objects.filter(assignment_id=assignment_id).exists()


@register.filter()
def absvalue(var):
    return abs(var)


@register.filter()
def times(var, times):
    return var * times


@register.filter()
def substract(var, sub):
    return var - sub
