import os

import yaml
from django.test import TestCase

from gui.assignments.forms import AssignmentsForm, TagsForm
from lmaa.settings import BASE_DIR

config_stream = open(os.path.join(BASE_DIR, 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']


class AssignmentsFormTest(TestCase):
    def test_form_valid(self):
        form = AssignmentsForm(data={
            'semester': 'F21',
            'sheet': 1,
            'task': 1,
            'assignment': 'Do something',
            'effort': 2,
            'scope': 4,
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form = AssignmentsForm(data={
            'semester': 'F21',
            'sheet': 1,
            'task': 1,
            'assignment': 'Do something' * 50,
            'effort': 6,
            'scope': -1,
        })
        self.assertFalse(form.is_valid())


class TagsFormTest(TestCase):
    def test_form_valid(self):
        form = TagsForm(data={
            'name': 'Homework',
        })
        self.assertTrue(form.is_valid())

    def test_form_invalid(self):
        form = TagsForm(data={
            'name': '',
        })
        self.assertFalse(form.is_valid())
