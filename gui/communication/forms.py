from django import forms
from django.forms import Textarea
from django_select2.forms import Select2MultipleWidget

from gui.assignments.models import Assignment, Solution
from gui.communication.models import LanguageModel, Property, PropertyType, SolutionRequest


class LanguageModelRequestForm(forms.Form):
    """
    Form for inputting basic request parameters (assignments [multiple choice], model [single choice])
    """

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
    """
    Form for dynamically inputting request parameters depending on the selected model.

    Automatically adds all request parameters to the form in __init__()
    """

    # Input for number of repeats
    repeats = forms.IntegerField(min_value=1, max_value=5, initial=1, required=True)

    def __init__(self, *args, **kwargs):
        """
        Fetches information about the requested language model and automatically adds all the models' request
        parameters
        """

        request_pk = kwargs.pop('req', None)
        super().__init__(*args, **kwargs)

        if SolutionRequest.objects.get(pk=request_pk):
            for prop in Property.objects.filter(language_model=SolutionRequest.objects.get(pk=request_pk).model):
                if prop.is_configuration:
                    # add model request property with type and required information
                    if prop.type == PropertyType.int:
                        self.fields[prop.name] = forms.IntegerField(required=prop.mandatory, initial=int(prop.default))
                    elif prop.type == PropertyType.float:
                        self.fields[prop.name] = forms.FloatField(required=prop.mandatory, initial=float(prop.default))
                    else:
                        self.fields[prop.name] = forms.CharField(required=prop.mandatory, initial=prop.default)


class LanguageModelRequestSolutionEditForm(forms.Form):
    """
    Form for displaying newly generated solutions.

    Automatically adds new solutions as form fields in __init__()
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add a form field for every solution marked as 'new'
        for solution in Solution.objects.filter(is_new=True):
            self.fields['sol' + str(solution.pk)] = forms.CharField(initial=solution.solution,
                                                                    widget=Textarea(attrs={'rows': 10}, ),
                                                                    label=solution.assignment.__str__())
