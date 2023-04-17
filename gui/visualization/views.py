from django.db.models.functions import datetime
from django.http import JsonResponse
from django.views.generic import TemplateView

from gui.assignments.models import Assignment, Solution
from gui.testing.models import Testresult, ContainsTestcase, CompilesTestcase, UnitTestcase


class VisualizationOverview(TemplateView):
    template_name = 'visualization/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assignments = Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask')
        current_assignment = assignments.first().id
        solutions = Solution.objects.filter(assignment_id=current_assignment).order_by('timestamp')

        context['assignments'] = assignments
        context['solutions'] = []

        return context


class VisualizeSingleSolution(TemplateView):
    template_name = 'visualization/display_solution.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solution_id = self.kwargs.get('pk')
        solution = Solution.objects.get(id=solution_id)
        context['solution'] = solution

        context['containsTestcases'] = ContainsTestcase.objects.filter(assignment_id=solution.assignment_id) \
            .order_by('phrase').all()
        context['test_results'] = self.__build_existing_test_results__(solution_id)
        context['has_compiles_testcase'] = CompilesTestcase.objects.filter(
            assignment_id=self.kwargs.get('ass')).exists()
        context['has_unit_testcase'] = UnitTestcase.objects.filter(assignment_id=self.kwargs.get('ass')).exists()

        return context

    def __build_existing_test_results__(self, solution_id: int) -> dict[
        datetime.datetime, dict[str, Testresult | dict[ContainsTestcase, Testresult]]]:
        """
            {
                timestamp_1: {
                    'compiles': Testresult,
                    'contains': {
                        ContainsTestcase1: Testresult,
                        ContainsTestcase2: Testresult,
                    }
                    'unit': Testresult
                },
                ...
            }
        """

        result = {}

        # get all executed timestamps for the assignment
        timestamps = Testresult.objects.filter(solution_id=solution_id) \
            .order_by('timestamp') \
            .values_list('timestamp', flat=True) \
            .distinct()
        assignment = Solution.objects.get(id=solution_id).assignment

        for ts in timestamps:
            result[ts] = {}

            compiles_test_cases = CompilesTestcase.objects.filter(assignment=assignment)
            compiles_test_results = Testresult.objects.filter(testcase__assignment_id=assignment.id,
                                                              solution_id=solution_id,
                                                              testcase__in=compiles_test_cases,
                                                              timestamp=ts)

            if compiles_test_results.exists():
                result[ts]['compiles'] = compiles_test_results.first()

            contains_test_cases = ContainsTestcase.objects.filter(assignment=assignment)
            contains_test_results = Testresult.objects.filter(testcase__assignment_id=assignment.id,
                                                              solution_id=solution_id,
                                                              testcase__in=contains_test_cases,
                                                              timestamp=ts)

            if contains_test_results.exists():
                result[ts]['contains'] = {}
                for ctr in contains_test_results:
                    ctc = ContainsTestcase.objects.get(id=ctr.testcase_id)
                    if ctc not in result[ts]['contains']:
                        result[ts]['contains'][ctc] = ctr

            unit_test_cases = UnitTestcase.objects.filter(assignment=assignment)
            unit_test_results = Testresult.objects.filter(testcase__assignment_id=assignment.id,
                                                          solution_id=solution_id,
                                                          testcase__in=unit_test_cases,
                                                          timestamp=ts)

            if unit_test_results.exists():
                result[ts]['unit'] = unit_test_results.first()

        return result


class SolutionWrapper():
    def __init__(self, id, timestamp, communicator) -> None:
        super().__init__()
        self.id = id
        self.timestamp = timestamp
        self.communicator = communicator

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'communicator': self.communicator
        }


def __get_wrapped_solutions__(queryset):
    solutions = []
    for solution in queryset:
        wrapped_solution = SolutionWrapper(solution.id, solution.timestamp, solution.communicator)
        solutions.append(wrapped_solution.to_dict())
    return solutions


def fetch_solutions_for_assignment(request, ass):
    response = {
        'solutions': __get_wrapped_solutions__(Solution.objects.filter(assignment_id=ass).all())
    }

    return JsonResponse(response)
