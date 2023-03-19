import os

import yaml
from django.forms import ModelForm, Textarea

from gui.assignments.models import Assignment
from lmaa.settings import BASE_DIR

config_stream = open(os.path.join(BASE_DIR, 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']


class AssignmentsCreateForm(ModelForm):
    class Meta:
        model = Assignment
        fields = '__all__'
        exclude = ['classification']
        widgets = {
            'assignment': Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(AssignmentsCreateForm, self).__init__(*args, **kwargs)
        self.fields['subtask'].required = False
