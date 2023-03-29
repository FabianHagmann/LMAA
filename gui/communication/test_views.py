from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.urls import reverse

from gui.assignments.models import Assignment
from gui.communication.models import LanguageModel, Property, PropertyType, SolutionRequest, \
    SolutionRequestStatus, SolutionRequestParameter


class LanguageModelRequestFormViewTest(TestCase):
    def setUp(self):
        self.url = reverse('communication')
        self.assignment = Assignment.objects.create(
            semester='2022SS',
            sheet=2,
            task=1,
            subtask='a',
            assignment='Test assignment',
            effort=3,
            scope=4
        )
        self.language_model = LanguageModel.objects.create(name='Test Model')

    def test_get_request_returns_form(self):
        response = self.client.get(self.url)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="assignments"')
        self.assertContains(response, 'name="models"')
        self.assertContains(response, 'name="csrfmiddlewaretoken"')

    def test_post_request_creates_solution_request(self):
        data = {
            'assignments': [self.assignment.id],
            'models': self.language_model.id,
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 302)
        solution_request = SolutionRequest.objects.first()
        self.assertIsNotNone(solution_request)
        self.assertEqual(solution_request.model, self.language_model)
        self.assertIn(self.assignment, solution_request.assignments.all())

    def test_post_request_redirects_to_configuration_view(self):
        data = {
            'assignments': [self.assignment.id],
            'models': self.language_model.id,
            'csrfmiddlewaretoken': 'testtoken'
        }
        response = self.client.post(self.url, data)
        self.assertRedirects(
            response,
            reverse('communication-configure', kwargs={'req': SolutionRequest.objects.first().id})
        )
