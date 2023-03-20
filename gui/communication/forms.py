from django import forms
from django_select2.forms import Select2MultipleWidget

from gui.assignments.models import Assignment


class LanguageModelRequestForm(forms.Form):
    assignments = forms.ModelMultipleChoiceField(
        queryset=Assignment.objects.all().order_by('semester', 'sheet', 'task', 'subtask'),
        widget=Select2MultipleWidget(attrs={
            'class': 'select2-bootstrap-5',
            'data-bs-select': 'multiple',
            'data-bs-container': 'body',
            'data-live-search': 'true',
            'data-placeholder': 'Choose tags',
        }),
    )

