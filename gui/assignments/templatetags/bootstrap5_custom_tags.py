from django import template, forms
from django.utils.safestring import mark_safe

"""
Custom Django text for templating
"""

register = template.Library()


@register.simple_tag(takes_context=True)
def bootstrap_form_group(context, field, addtl_classes=''):
    """
    Creates a custom bootstrap-styled input tag
    :param field: django form field to be displayed
    :param addtl_classes: additional css classes to be used in the form field
    :return: marked safe html for template
    """
    css_classes = ' '.join([
        'form-group',
        addtl_classes,
        'has-danger' if field.errors else '',
    ])
    label = field.label_tag(attrs={'class': 'form-label'})
    widget = field.field.widget
    if isinstance(widget, (forms.TextInput, forms.Select, forms.NumberInput, forms.Textarea)):
        widget_attrs = widget.attrs
        widget_attrs['class'] = f'{widget_attrs.get("class", "")} form-control'
    return mark_safe(f'<div class="{css_classes}">{label}{field}</div>')


@register.simple_tag(takes_context=True)
def bootstrap_form_group_no_label(context, field, addtl_classes=''):
    """
    Creates a custom bootstrap-styled input tag without a label
    :param field: django form field to be displayed
    :param addtl_classes: additional css classes to be used in the form field
    :return: marked safe html for template
    """
    css_classes = ' '.join([
        'form-group',
        addtl_classes,
        'has-danger' if field.errors else '',
    ])
    widget = field.field.widget
    if isinstance(widget, (forms.TextInput, forms.Select, forms.NumberInput, forms.Textarea)):
        widget_attrs = widget.attrs
        widget_attrs['class'] = f'{widget_attrs.get("class", "")} form-control'
    return mark_safe(f'<div class="{css_classes}">{field}</div>')
