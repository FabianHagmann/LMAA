import os

import yaml
from django.forms import ModelForm, Textarea

from gui.assignments.models import Assignment, Tag
from lmaa.settings import BASE_DIR

config_stream = open(os.path.join(BASE_DIR, 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']


class AssignmentsForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'
        exclude = ['classification']
        widgets = {
            'assignment': Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(AssignmentsForm, self).__init__(*args, **kwargs)
        self.fields['subtask'].required = False


class TagsForm(ModelForm):

    class Meta:
        model = Tag
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(TagsForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = True
