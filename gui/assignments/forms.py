import os

import yaml
from django import forms
from django.forms import ModelForm, Textarea
from django_select2.forms import Select2MultipleWidget

from gui.assignments.models import Assignment, Tag
from lmaa.settings import BASE_DIR

config_stream = open(os.path.join(BASE_DIR, 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']


class AssignmentsForm(ModelForm):
    """
    ModelForm for all fields of 'Assignment'. Contains all fields of Assignment including foreign keys and classification
    """

    # multiselect for Tags
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all().order_by('name'),
        widget=Select2MultipleWidget(attrs={
            'class': 'select2-bootstrap-5',
            'data-bs-select': 'multiple',
            'data-bs-container': 'body',
            'data-live-search': 'true',
            'data-placeholder': 'Choose tags',
        }),
    )

    class Meta:
        model = Assignment
        fields = '__all__'
        widgets = {
            'assignment': Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        """
        Init method. Sets optional fields to not-required
        """
        super(AssignmentsForm, self).__init__(*args, **kwargs)
        self.fields['subtask'].required = False
        self.fields['effort'].required = False
        self.fields['scope'].required = False
        self.fields['tags'].required = False


class TagsForm(ModelForm):
    """
    ModelForm for all fields of Tags
    """

    class Meta:
        model = Tag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        """
        Init method. Sets mandatory fields to required
        """
        super(TagsForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
