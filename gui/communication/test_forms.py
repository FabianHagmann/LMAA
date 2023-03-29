from django.test import TestCase
from django.utils.datetime_safe import datetime

from gui.assignments.models import Assignment, Solution
from gui.communication.forms import LanguageModelRequestForm, LanguageModelRequestConfigurationForm, \
    LanguageModelRequestSolutionEditForm
from gui.communication.models import LanguageModel, Property, PropertyType, SolutionRequest


class LanguageModelRequestFormTest(TestCase):
    def setUp(self):
        self.assignment = Assignment.objects.create(semester='2022SS',
                                                    sheet=2,
                                                    task=1,
                                                    subtask='a',
                                                    assignment='Test assignment',
                                                    effort=3,
                                                    scope=4)
        self.model = LanguageModel.objects.create(name='Test Model')

    def test_valid_form(self):
        form_data = {'assignments': [self.assignment.pk], 'models': self.model.pk}
        form = LanguageModelRequestForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_missing_assignments(self):
        form_data = {'models': self.model.pk}
        form = LanguageModelRequestForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_missing_model(self):
        form_data = {'assignments': [self.assignment.pk]}
        form = LanguageModelRequestForm(data=form_data)
        self.assertFalse(form.is_valid())


class LanguageModelRequestSolutionEditFormTest(TestCase):
    def setUp(self):
        self.assignment = Assignment.objects.create(semester='2022SS',
                                                    sheet=2,
                                                    task=1,
                                                    subtask='a',
                                                    assignment='Test assignment',
                                                    effort=3,
                                                    scope=4)
        self.solution = Solution.objects.create(assignment=self.assignment, solution='Test Solution', is_new=True,
                                                timestamp=datetime.now())

    def test_form_fields(self):
        form = LanguageModelRequestSolutionEditForm()
        self.assertTrue('sol{}'.format(self.solution.pk) in form.fields)
