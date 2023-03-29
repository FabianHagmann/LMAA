from django.test import TestCase

from gui.communication.models import LanguageModel, Property, SolutionRequest


class LanguageModelModelTest(TestCase):
    def setUp(self):
        LanguageModel.objects.create(name="Test Model")

    def test_language_model_str(self):
        test_model = LanguageModel.objects.get(name="Test Model")
        self.assertEqual(str(test_model), "Test Model")


class PropertyModelTest(TestCase):
    def setUp(self):
        self.language_model = LanguageModel.objects.create(name="Test Model")
        Property.objects.create(name="Test Property", type=1, mandatory=True, default="0",
                                language_model=self.language_model)

    def test_property_str(self):
        test_property = Property.objects.get(name="Test Property")
        self.assertEqual(str(test_property), "Test Property")


class SolutionRequestModelTest(TestCase):
    def setUp(self):
        self.language_model = LanguageModel.objects.create(name="Test Model")
        self.solution_request = SolutionRequest.objects.create(model=self.language_model, status=1, repeats=1)

    def test_solution_request_timestamp(self):
        self.assertIsNotNone(self.solution_request.timestamp)

    def test_solution_request_default_status(self):
        self.assertEqual(self.solution_request.status, 1)

    def test_solution_request_default_repeats(self):
        self.assertEqual(self.solution_request.repeats, 1)

    def test_solution_request_assignments(self):
        self.solution_request.assignments.create(semester='2022SS',
                                                 sheet=2,
                                                 task=1,
                                                 subtask='a',
                                                 assignment='Test assignment',
                                                 effort=3,
                                                 scope=4)
        self.assertEqual(self.solution_request.assignments.count(), 1)

    def test_solution_request_parameters(self):
        self.solution_request.parameters.create(key="param1", value="value1")
        self.assertEqual(self.solution_request.parameters.count(), 1)
