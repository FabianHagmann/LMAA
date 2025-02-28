from django import forms
from django.core.exceptions import ValidationError

from gui.assignments.models import Assignment
from gui.testing.models import CompilesTestcase, UnitTestcase


class JavaFileValidator:
    """
    Validator to check if the filetype of any file-input is ".java"
    """

    def __call__(self, value):
        if not value.name.endswith('.java'):
            raise ValidationError('Only .java files are allowed.')


class AssignmentTestcasesForm(forms.Form):
    """
    Form containing all types of testcases available for an assignment
    """
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
        """
        Init method. Sets compiles and unit testcases in accordance to the database entry
        """

        # pop custom kwargs and call super init
        assignment_pk = kwargs.pop('ass', None)
        super().__init__(*args, **kwargs)

        if Assignment.objects.get(pk=assignment_pk):
            if CompilesTestcase.objects.filter(assignment_id=assignment_pk).exists() and \
                    CompilesTestcase.objects.filter(assignment_id=assignment_pk).get().active:
                self.fields['compilesTestcase'].initial = '1'
            else:
                self.fields['compilesTestcase'].initial = '0'

            if UnitTestcase.objects.filter(assignment_id=assignment_pk).exists():
                self.fields['unitTestcase'].initial = UnitTestcase.objects.filter(
                    assignment_id=assignment_pk).first().file


class ContainsTestcaseCreateForm(forms.Form):
    """
    Form for adding or editing a contains testcase
    """
    phrase = forms.CharField(max_length=64, required=True)
    times = forms.IntegerField(min_value=0, max_value=10, required=True, initial=1)
