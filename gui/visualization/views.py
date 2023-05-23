import os
import statistics
from datetime import datetime

import numpy as np
from django.http import JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from numpy import ndarray

from gui.assignments.models import Assignment, Solution, Tag
from gui.testing.models import ContainsTestcase, CompilesTestcase, UnitTestcase, CompilesTestresult, ContainsTestresult, \
    UnitTestresult
from gui.visualization.forms import SolutionEditForm
from gui.visualization.tasks import __get_report_folder_path__, generate_similarity_report_for_export
from scripts.visualization.metrics import metrics_manager as manager
from scripts.visualization.metrics.success_metric import UnweightedTestResult


class VisualizationOverview(TemplateView):
    template_name = 'visualization/overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        page = int(self.request.GET.get('page', 1))
        page_size = 10

        assignments = Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask')[
                      page_size * (page - 1):(page_size * page)]

        context['assignments'] = assignments
        context['solutions'] = []
        context['page_obj'] = self.__build_page_obj__(page, page_size)

        return context

    @staticmethod
    def __build_page_obj__(page, page_size):
        page_obj = {}
        num_assignments = Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask').count()
        max_pages = round(num_assignments / page_size) if (num_assignments % page_size == 0) else round(
            num_assignments / page_size) + 1

        page_obj.__setitem__('has_previous', page != 1)
        page_obj.__setitem__('previous_page_number', page - 1)
        page_obj.__setitem__('number', page)
        page_obj.__setitem__('num_pages', max_pages)
        page_obj.__setitem__('has_next', page != max_pages)
        page_obj.__setitem__('next_page_number', page + 1)

        return page_obj


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

        prepared_solutions_with_ids = self.__prepare_assignment_solutions_single_source_with_ids__(solutions)
        single_source_mccabe_complexity = man.mccabe_complexity(prepared_solutions_with_ids)
        single_source_halstead_complexity = man.halstead_metrics(prepared_solutions_with_ids)
        halstead_volume_list = self.__prepare_halstead_volume_list__(single_source_halstead_complexity)

        context['single_source_cosine_sim_matrix'] = single_source_cosine_sim_matrix
        context['single_source_cosine_total_average'] = single_source_cosine_total_average
        context['single_source_cosine_total_median'] = single_source_cosine_total_median
        context['single_source_mccabe_complexity'] = single_source_mccabe_complexity
        context['single_source_halstead_complexity'] = single_source_halstead_complexity
        context['single_source_mccabe_complexity_mean'] = statistics.mean(single_source_mccabe_complexity.values())
        context['single_source_mccabe_complexity_sd'] = statistics.stdev(single_source_mccabe_complexity.values())
        context['single_source_halstead_volume_mean'] = statistics.mean(halstead_volume_list)
        context['single_source_halstead_volume_sd'] = statistics.stdev(halstead_volume_list)
        context['single_source_mccabe_complexity_steps'] = np.linspace(min(single_source_mccabe_complexity.values()),
                                                                       max(single_source_mccabe_complexity.values()), 6)
        context['single_source_halstead_volume_steps'] = np.linspace(min(halstead_volume_list),
                                                                     max(halstead_volume_list), 6)

    def __prepare_assignment_solutions_single_source__(self, solutions):
        prepared_solutions = []
        for solution in solutions:
            prepared_solutions.append(solution.solution)
        return prepared_solutions

    def __prepare_assignment_solutions_single_source_with_ids__(self, solutions):
        prepared_solutions = {}
        for solution in solutions:
            prepared_solutions.__setitem__(solution.id, solution.solution)
        return prepared_solutions

    def __prepare_halstead_volume_list__(self, single_source_halstead_complexity):
        volume_list = []
        for metric in single_source_halstead_complexity.values():
            volume_list.append(metric.get('Program Volume'))
        return volume_list


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


class TestMetricVisualizationView(TemplateView):
    template_name = 'visualization/success/success_metric_overview.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['metrics'] = self.__prepare_metrics__()
        context['overall_success_rate'] = context['metrics']['overall_success_rate']
        context['metrics'].pop('overall_success_rate')

        return context

    def __prepare_metrics__(self) -> dict[Tag, dict[str, any]]:
        man = manager.MetricsManager()
        success_metrics = {}

        compiles_test_results_overall = []
        for tag in Tag.objects.all().order_by('name'):
            assignments_with_tag = Assignment.objects.filter(tags=tag)

            compiles_test_results_for_tag = []
            for assignment in assignments_with_tag:
                newest_compile, newest_contains, newest_unit = self.__get_newest_timestamps_for_assignment__(assignment)

                compiles_test_results_for_assignment = []
                if newest_compile is not None:
                    for testresult in UnweightedTestResult.fromCompilesTestresults(
                            CompilesTestresult.objects.filter(solution__assignment=assignment,
                                                              timestamp=newest_compile)):
                        compiles_test_results_for_assignment.append(testresult)

                if len(compiles_test_results_for_assignment) > 0:
                    compiles_test_results_for_tag.append(compiles_test_results_for_assignment)
                    compiles_test_results_overall.append(compiles_test_results_for_assignment)

            single_tag_metrics = {}
            single_tag_metrics.__setitem__('num_assignments', len(assignments_with_tag))

            if len(compiles_test_results_for_tag) > 0:
                tag_success_metric = man.success_rate_compiles(compiles_test_results_for_tag)
                single_tag_metrics.__setitem__('tag_success_rate', tag_success_metric)
            else:
                single_tag_metrics.__setitem__('tag_success_rate', '')

            success_metrics.__setitem__(tag, single_tag_metrics)

        success_metrics.__setitem__('overall_success_rate', man.success_rate_compiles(compiles_test_results_overall))
        return success_metrics

    def __get_newest_timestamps_for_assignment__(self, assignment: Assignment):
        newest_compile = CompilesTestresult.objects.filter(solution__assignment=assignment).order_by('-timestamp')
        newest_contains = ContainsTestresult.objects.filter(solution__assignment=assignment).order_by('-timestamp')
        newest_unit = UnitTestresult.objects.filter(solution__assignment=assignment).order_by('-timestamp')

        newest_compile_timestamp = newest_compile.first().timestamp if newest_compile.exists() else None
        newest_contains_timestamp = newest_contains.first().timestamp if newest_contains.exists() else None
        newest_unit_timestamp = newest_unit.first().timestamp if newest_unit.exists() else None

        return newest_compile_timestamp, newest_contains_timestamp, newest_unit_timestamp


class VisualizationCompareView(TemplateView):
    template_name = 'visualization/compare_solutions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        first_solution_id = self.kwargs.get('sol1')
        second_solution_id = self.kwargs.get('sol2')
        first_solution = Solution.objects.get(id=first_solution_id)
        second_solution = Solution.objects.get(id=second_solution_id)

        context['first_solution'] = first_solution
        context['second_solution'] = second_solution

        return context


def export_similarity_report(request):
    file_path = os.path.join(__get_report_folder_path__(), 'similarity_report.csv')

    generate_similarity_report_for_export()

    with open(file_path, 'r') as report:
        response = HttpResponse(report.read(), content_type="text/csv")
        response['Content-Disposition'] = "attachment;filename=similarity_report.csv"
        return response

