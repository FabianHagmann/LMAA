from django.test import TestCase, Client
from django.urls import reverse

from gui.assignments.models import Assignment, Tag


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.assignments_url = reverse('assignments')
        self.tags_url = reverse('tags')

    def test_assignments_GET(self):
        response = self.client.get(self.assignments_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'assignments/assignment_main.html')

    def test_create_assignment_POST(self):
        response = self.client.post(reverse('assignments-create'), {
            'semester': '2021WS',
            'sheet': 1,
            'task': 1,
            'subtask': 'a',
            'assignment': 'Test assignment',
            'effort': 3,
            'scope': 4,
            'tags': []
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Assignment.objects.count(), 1)

    def test_edit_assignment_POST(self):
        assignment = Assignment.objects.create(
            semester='2022SS',
            sheet=2,
            task=1,
            subtask='a',
            assignment='Test assignment',
            effort=3,
            scope=4
        )

        response = self.client.post(reverse('assignments-edit', args=[assignment.id]), {
            'semester': '2022WS',
            'sheet': 3,
            'task': 2,
            'subtask': 'b',
            'assignment': 'Updated test assignment',
            'effort': 4,
            'scope': 5,
            'tags': []
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Assignment.objects.first().semester, '2022WS')
        self.assertEquals(Assignment.objects.first().sheet, 3)
        self.assertEquals(Assignment.objects.first().task, 2)
        self.assertEquals(Assignment.objects.first().subtask, 'b')
        self.assertEquals(Assignment.objects.first().assignment, 'Updated test assignment')
        self.assertEquals(Assignment.objects.first().effort, 4)
        self.assertEquals(Assignment.objects.first().scope, 5)

    def test_delete_assignment_POST(self):
        assignment = Assignment.objects.create(
            semester='2022WS',
            sheet=1,
            task=1,
            subtask='a',
            assignment='Test assignment',
            effort=3,
            scope=4
        )

        response = self.client.post(reverse('assignments-delete', args=[assignment.id]))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Assignment.objects.count(), 0)

    def test_tags_GET(self):
        response = self.client.get(self.tags_url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'assignments/tags/tag_main.html')

    def test_create_tag_POST(self):
        response = self.client.post(reverse('tags-create'), {
            'name': 'Test tag'
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Tag.objects.count(), 1)

    def test_edit_tag_POST(self):
        tag = Tag.objects.create(name='Test tag')

        response = self.client.post(reverse('tags-edit', args=[tag.id]), {
            'name': 'Updated test tag'
        })

        self.assertEquals(response.status_code, 302)
        self.assertEquals(Tag.objects.first().name, 'Updated test tag')
