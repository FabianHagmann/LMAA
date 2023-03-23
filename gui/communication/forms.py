from django import forms
from django.forms import Textarea
from django_select2.forms import Select2MultipleWidget, ModelSelect2Widget

from gui.assignments.models import Assignment, Solution
from gui.communication.models import LanguageModel, Property, PropertyType, SolutionRequest


class LanguageModelRequestForm(forms.Form):
    assignments = forms.ModelMultipleChoiceField(
        queryset=Assignment.objects.all().order_by('semester', 'sheet', 'task', 'subtask'),
        widget=Select2MultipleWidget(attrs={
            'class': 'select2-bootstrap-5',
            'data-bs-select': 'multiple',
            'data-bs-container': 'body',
            'data-live-search': 'true',
            'data-placeholder': 'Choose assignments',
        }),
    )
    models = forms.ModelChoiceField(
        queryset=LanguageModel.objects.order_by('name'),
    )


class LanguageModelRequestConfigurationForm(forms.Form):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if SolutionRequest.objects.order_by('timestamp').exists():
            for prop in Property.objects.filter(
                    language_model__name=SolutionRequest.objects.order_by('timestamp').first().model.name):
                if prop.is_configuration:
                    if prop.type == PropertyType.int:
                        self.fields[prop.name] = forms.IntegerField(required=prop.mandatory, initial=int(prop.default))
                    elif prop.type == PropertyType.float:
                        self.fields[prop.name] = forms.FloatField(required=prop.mandatory, initial=float(prop.default))
                    else:
                        self.fields[prop.name] = forms.CharField(required=prop.mandatory, initial=prop.default)


class LanguageModelRequestSolutionEditForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for solution in Solution.objects.filter(is_new=True):
            self.fields['sol' + str(solution.pk)] = forms.CharField(initial=solution.solution,
                                                                    widget=Textarea(attrs={'rows': 10}, ),
                                                                    label=solution.assignment.__str__())
