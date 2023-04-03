from django import forms
from django.core.exceptions import ValidationError

from gui.assignments.models import Assignment
from gui.testing.models import CompilesTestcase, UnitTestcase, ContainsTestcase


class JavaFileValidator:
    def __call__(self, value):
        if not value.name.endswith('.java'):
            raise ValidationError('Only .java files are allowed.')


class AssignmentTestcasesForm(forms.Form):
    radio_choices = [('0', 'Inactive'), ('1', 'Active')]

    compilesTestcase = forms.ChoiceField(
        widget=forms.RadioSelect,
        choices=radio_choices
    )
    unitTestcase = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={
                'multiple': False
            }
        ),
        required=False,
        validators=[JavaFileValidator()]
    )

    def __init__(self, *args, **kwargs):
        # pop custom kwargs and call super init
        assignment_pk = kwargs.pop('ass', None)
        super().__init__(*args, **kwargs)

        if Assignment.objects.get(pk=assignment_pk):
            if CompilesTestcase.objects.filter(assignment_id=assignment_pk).exists() and \
                    CompilesTestcase.objects.filter(assignment_id=assignment_pk).get().active:
                self.fields['compilesTestcase'].initial = '1'
            else:
                self.fields['compilesTestcase'].initial = '0'

            for i, cont_testcase in enumerate(ContainsTestcase.objects.filter(assignment_id=assignment_pk).all()):
                self.fields['containsTestcasePhrase{}'.format(i)] = forms.CharField(
                    max_length=64,
                    required=True,
                    initial=cont_testcase.phrase
                )
                self.fields['containsTestcaseTimes{}'.format(i)] = forms.IntegerField(
                    max_value=10,
                    min_value=0,
                    required=True,
                    initial=cont_testcase.times
                )

            if UnitTestcase.objects.filter(assignment_id=assignment_pk).exists():
                self.fields['unitTestcase'].initial = UnitTestcase.objects.filter(
                    assignment_id=assignment_pk).first().file

    def get_contains_testcases(self, assignment_pk):
        contains_testcases = []

        # get the input values for each ContainsTestcase instance
        for i, cont_testcase in enumerate(ContainsTestcase.objects.filter(assignment_id=assignment_pk).all()):
            phrase_key = 'containsTestcasePhrase{}'.format(i)
            times_key = 'containsTestcaseTimes{}'.format(i)
            phrase_value = self.cleaned_data.get(phrase_key)
            times_value = self.cleaned_data.get(times_key)
            if phrase_value and times_value:
                cont_testcase.phrase = phrase_value
                cont_testcase.times = times_value
                contains_testcases.append(cont_testcase)

        return contains_testcases
