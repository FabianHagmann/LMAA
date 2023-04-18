from datetime import datetime

from django.http import JsonResponse
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from numpy import ndarray

from gui.assignments.models import Assignment, Solution
from gui.testing.models import ContainsTestcase, CompilesTestcase, UnitTestcase, CompilesTestresult, ContainsTestresult, \
    UnitTestresult
from gui.visualization.forms import SolutionEditForm
from scripts.visualization.metrics import metrics_manager as manager


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
            assignment_id=solution.assignment_id).exists()
        context['has_unit_testcase'] = UnitTestcase.objects.filter(assignment_id=solution.assignment_id).exists()

        return context

    def __build_existing_test_results__(self, solution_id: int):
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
        timestamps_compiles = CompilesTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_contains = ContainsTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_unit = UnitTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps = set(timestamps_compiles.union(timestamps_contains, timestamps_unit).order_by('timestamp'))

        assignment = Solution.objects.get(id=solution_id).assignment

        for ts in timestamps:
            result[ts] = {}

            compiles_test_cases = CompilesTestcase.objects.filter(assignment=assignment)
            compiles_test_results = CompilesTestresult.objects.filter(testcase__assignment_id=assignment.id,
                                                                      solution_id=solution_id,
                                                                      testcase__in=compiles_test_cases,
                                                                      timestamp=ts)

            if compiles_test_results.exists():
                result[ts]['compiles'] = compiles_test_results.first()

            contains_test_cases = ContainsTestcase.objects.filter(assignment=assignment)
            contains_test_results = ContainsTestresult.objects.filter(testcase__assignment_id=assignment.id,
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
            unit_test_results = UnitTestresult.objects.filter(testcase__assignment_id=assignment.id,
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


class AssignmentSimilarity(TemplateView):
    template_name = 'visualization/similarity/assignment_similarity.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assignment_id = self.kwargs.get('ass')
        context['assignment'] = Assignment.objects.get(id=assignment_id)
        self.__get_similarity_metrics__(context)

        return context

    def __get_similarity_metrics__(self, context):
        communicators = Solution.objects.filter(assignment=context['assignment']) \
            .values_list('communicator', flat=True) \
            .distinct()
        context['communicators'] = communicators

        solutions = Solution.objects.filter(assignment=context['assignment']).all()
        context['solutions'] = solutions

        man = manager.MetricsManager()

        prepared_solutions = self.__prepare_assignment_solutions_single_source__(solutions)
        single_source_cosine_sim_matrix = man.similarity_cosine_single_source(prepared_solutions)
        single_source_cosine_total_average = man.similarity_cosine_average(solutions.count(),
                                                                           single_source_cosine_sim_matrix)
        single_source_cosine_total_median = man.similarity_cosine_median(solutions.count(),
                                                                         single_source_cosine_sim_matrix)

        context['single_source_cosine_sim_matrix'] = single_source_cosine_sim_matrix
        context['single_source_cosine_total_average'] = single_source_cosine_total_average
        context['single_source_cosine_total_median'] = single_source_cosine_total_median

    def __prepare_assignment_solutions_single_source__(self, solutions):
        prepared_solutions = []
        for solution in solutions:
            prepared_solutions.append(solution.solution)
        return prepared_solutions


def __get_wrapped_array__(cosine_sim_matrix: ndarray):
    return list(cosine_sim_matrix.flatten())


def fetch_assignment_similarity_for_communicator(request, ass, com):
    prepared_solutions = {}
    solutions = Solution.objects.filter(assignment_id=ass, communicator=com).all()
    man = manager.MetricsManager()

    # prepare solutions for similarity check
    prepared_solutions = []
    for solution in solutions:
        prepared_solutions.append(solution.solution)

    cosine_sim_matrix = man.similarity_cosine_single_source(prepared_solutions)
    cosine_total_average = man.similarity_cosine_average(solutions.count(), cosine_sim_matrix)
    cosine_total_median = man.similarity_cosine_median(solutions.count(), cosine_sim_matrix)

    response = {
        'solutions': __get_wrapped_solutions__(solutions),
        'cosine_total_average': cosine_total_average,
        'cosine_total_median': cosine_total_median,
        'cosine_sim_matrix': __get_wrapped_array__(cosine_sim_matrix)
    }

    return JsonResponse(response)


class EditSingleSolution(FormView):
    template_name = 'visualization/edit_solution.html'
    form_class = SolutionEditForm

    def __init__(self, **kwargs):
        super(FormView, self).__init__(**kwargs)
        self.success_pk = None

    def get_initial(self):
        initial = super().get_initial()

        initial['solution'] = Solution.objects.get(id=self.kwargs.get('pk')).solution

        return initial

    def get_success_url(self):
        return reverse(
            'visualize-solution',
            kwargs={
                'pk': self.kwargs.get('pk')
            }
        )

    def form_valid(self, form):
        existing_solution = Solution.objects.get(id=self.kwargs.get('pk'))

        existing_solution.solution = form.cleaned_data['solution']
        existing_solution.timestamp = datetime.now()

        existing_solution.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        solution_id = self.kwargs.get('pk')
        solution = Solution.objects.get(id=solution_id)
        context['solution'] = solution
        self.success_pk = solution_id

        context['containsTestcases'] = ContainsTestcase.objects.filter(assignment_id=solution.assignment_id) \
            .order_by('phrase').all()
        context['test_results'] = self.__build_existing_test_results__(solution_id)
        context['has_compiles_testcase'] = CompilesTestcase.objects.filter(
            assignment_id=solution.assignment_id).exists()
        context['has_unit_testcase'] = UnitTestcase.objects.filter(assignment_id=solution.assignment_id).exists()

        return context

    def __build_existing_test_results__(self, solution_id: int):
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
        timestamps_compiles = CompilesTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_contains = ContainsTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_unit = UnitTestresult.objects.filter(solution_id=solution_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps = set(timestamps_compiles.union(timestamps_contains, timestamps_unit).order_by('timestamp'))

        assignment = Solution.objects.get(id=solution_id).assignment

        for ts in timestamps:
            result[ts] = {}

            compiles_test_cases = CompilesTestcase.objects.filter(assignment=assignment)
            compiles_test_results = CompilesTestresult.objects.filter(testcase__assignment_id=assignment.id,
                                                                      solution_id=solution_id,
                                                                      testcase__in=compiles_test_cases,
                                                                      timestamp=ts)

            if compiles_test_results.exists():
                result[ts]['compiles'] = compiles_test_results.first()

            contains_test_cases = ContainsTestcase.objects.filter(assignment=assignment)
            contains_test_results = ContainsTestresult.objects.filter(testcase__assignment_id=assignment.id,
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
            unit_test_results = UnitTestresult.objects.filter(testcase__assignment_id=assignment.id,
                                                              solution_id=solution_id,
                                                              testcase__in=unit_test_cases,
                                                              timestamp=ts)

            if unit_test_results.exists():
                result[ts]['unit'] = unit_test_results.first()

        return result
