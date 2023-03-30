from django.views.generic import TemplateView

from gui.assignments.models import Assignment
from gui.testing.models import CompilesTestcase, ContainsTestcase, UnitTestcase


class AssignmentWithTestcases:
    def __init__(self, assignment: Assignment = None, compiles_testcase_active: bool = False,
                 contains_testcases: int = 0, unit_testcase_active: bool = False) -> None:
        self.assignment = assignment
        self.compiles_testcase = compiles_testcase_active
        self.contains_testcases = contains_testcases
        self.unit_testcase = unit_testcase_active
        super().__init__()


class TestcaseListView(TemplateView):
    template_name = 'testing/testcase_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assignments_with_testcases = self.__build_assignments_with_testcases_list()
        context['assignments'] = assignments_with_testcases

        return context

    @staticmethod
    def __build_assignments_with_testcases_list():
        assignments = []
        for ass in Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask'):
            compiles_testcase_active = CompilesTestcase.objects.filter(assignment=ass).exists()
            contains_testcases = ContainsTestcase.objects.filter(assignment=ass).count()
            unit_testcase_active = UnitTestcase.objects.filter(assignment=ass).exists()

            assignments.append(
                AssignmentWithTestcases(ass, compiles_testcase_active, contains_testcases, unit_testcase_active))
        return assignments


def __build_testcase_list_context__():
    pass
