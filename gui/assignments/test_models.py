from django.test import TestCase

from gui.assignments.models import Assignment, Tag


class TagTest(TestCase):
    def test_str_method(self):
        tag = Tag.objects.create(name='Homework')
        self.assertEqual(str(tag), 'Homework')


class AssignmentTest(TestCase):
    def test_str_method(self):
        assignment = Assignment.objects.create(
            semester='F21',
            sheet=1,
            task=1,
            assignment='Do something',
            effort=2,
            scope=4,
        )
        self.assertEqual(str(assignment), 'F21-AB1-1')

    def test_fields(self):
        assignment = Assignment.objects.create(
            semester='F21',
            sheet=1,
            task=1,
            assignment='Do something',
            effort=2,
            scope=4,
        )
        self.assertEqual(assignment.semester, 'F21')
        self.assertEqual(assignment.sheet, 1)
        self.assertEqual(assignment.task, 1)
        self.assertEqual(assignment.assignment, 'Do something')
        self.assertEqual(assignment.effort, 2)
        self.assertEqual(assignment.scope, 4)
