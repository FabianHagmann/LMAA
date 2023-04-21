import datetime

from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView, FormView, ListView, DeleteView

from gui.assignments.models import Assignment, Solution
from gui.testing.forms import AssignmentTestcasesForm, ContainsTestcaseCreateForm
from gui.testing.models import CompilesTestcase, ContainsTestcase, UnitTestcase, CompilesTestresult, ContainsTestresult, \
    UnitTestresult
from gui.testing.tasks import TestingExecutionThread


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

        page = int(self.request.GET.get('page', 1))
        page_size = 10

        assignments_with_testcases = self.__build_assignments_with_testcases_list(page, page_size)
        context['assignments'] = assignments_with_testcases
        context['page_obj'] = self.__build_page_obj__(page, page_size)

        return context

    @staticmethod
    def __build_assignments_with_testcases_list(page: int, page_size: int):
        assignments = []
        for ass in Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask')[page_size * (page - 1):(page_size * page)]:
            compiles_testcase_active = CompilesTestcase.objects.filter(assignment=ass, active=True).exists()
            contains_testcases = ContainsTestcase.objects.filter(assignment=ass).count()
            unit_testcase_active = UnitTestcase.objects.filter(assignment=ass).exists()

            assignments.append(
                AssignmentWithTestcases(ass, compiles_testcase_active, contains_testcases, unit_testcase_active))
        return assignments

    @staticmethod
    def __build_page_obj__(page, page_size):
        page_obj = {}
        num_assignments = Assignment.objects.order_by('semester', 'sheet', 'task', 'subtask').count()
        max_pages = round(num_assignments/page_size) if (num_assignments % page_size == 0) else round(num_assignments/page_size) + 1

        page_obj.__setitem__('has_previous', page != 1)
        page_obj.__setitem__('previous_page_number', page - 1)
        page_obj.__setitem__('number', page)
        page_obj.__setitem__('num_pages', max_pages)
        page_obj.__setitem__('has_next', page != max_pages)
        page_obj.__setitem__('next_page_number', page + 1)

        return page_obj


class TestcaseDetailsView(FormView):
    form_class = AssignmentTestcasesForm
    template_name = 'testing/testcase_details.html'
    success_url = '/testing'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.assignment = None

    def form_valid(self, form):
        assignment_pk = self.get_form_kwargs().get('ass')

        self.__update_or_create_compiles_testcase(assignment_pk, form.cleaned_data['compilesTestcase'])
        self.__update_or_create_unit_testcase(assignment_pk, self.request.FILES.get('unitTestcase'))

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(TestcaseDetailsView, self).get_form_kwargs()

        assignment_pk = self.kwargs['ass']
        self.assignment = Assignment.objects.get(pk=assignment_pk)
        kwargs.__setitem__('ass', assignment_pk)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['assignment_pk'] = self.kwargs.get('ass')
        context['containsTestcases'] = ContainsTestcase.objects.filter(assignment_id=self.kwargs['ass']) \
            .order_by('phrase').all()

        context['existing_test_results'] = self.__build_existing_test_results__(self.kwargs.get('ass'))
        context['existing_solutions'] = Solution.objects.filter(assignment_id=self.kwargs.get('ass'))
        context['existing_solutions_range'] = range(len(context['existing_solutions']))

        return context

    @staticmethod
    def __update_or_create_compiles_testcase(assignment_pk, updated_value):
        testcase_exists = CompilesTestcase.objects.filter(assignment_id=assignment_pk).exists()

        if testcase_exists:
            existing_testcase = CompilesTestcase.objects.filter(assignment_id=assignment_pk).first()
            existing_testcase.active = True if int(updated_value) else False
            existing_testcase.save()
        else:
            new_testcase = CompilesTestcase(assignment_id=assignment_pk, active=updated_value)
            new_testcase.save()

    @staticmethod
    def __update_or_create_unit_testcase(assignment_pk, updated_file):
        testcase_exists = UnitTestcase.objects.filter(assignment_id=assignment_pk).exists()

        if testcase_exists:
            if updated_file is None:
                UnitTestcase.objects.filter(assignment_id=assignment_pk).delete()
            else:
                existing_testcase = UnitTestcase.objects.filter(assignment_id=assignment_pk).first()
                existing_testcase.file = updated_file
                existing_testcase.save()
        elif updated_file is not None:
            new_testcase = UnitTestcase(assignment_id=assignment_pk, file=updated_file)
            new_testcase.save()

    def __build_existing_test_results__(self, assignment_id: int) -> dict[datetime.datetime, dict[str, dict[any, any]]]:
        """
            {
                timestamp_1: {
                    'compiles': {
                        solution_1: Testresult,
                        solution_2: Testresult,
                        ...
                    },
                    'contains': {
                        ContainsTestcase1: {
                            solution_1: Testresult,
                            solution_2: Testresult,
                            ...
                        },
                        ContainsTestcase1: {
                            solution_1: Testresult,
                            solution_2: Testresult,
                            ...
                        },
                        ...
                    },
                    'unit': {
                        solution_1: Testresult,
                        solution_2: Testresult,
                        ...
                    }
                },
                ...
            }
        """

        result = {}

        # get all executed timestamps for the assignment
        timestamps_compiles = CompilesTestresult.objects.filter(testcase__assignment_id=assignment_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_contains = ContainsTestresult.objects.filter(testcase__assignment_id=assignment_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps_unit = UnitTestresult.objects.filter(testcase__assignment_id=assignment_id) \
            .values_list('timestamp', flat=True) \
            .distinct()
        timestamps = set(timestamps_compiles.union(timestamps_contains, timestamps_unit).order_by('timestamp'))

        for ts in timestamps:
            result[ts] = {}

            compiles_test_cases = CompilesTestcase.objects.filter(assignment_id=assignment_id)
            compiles_test_results = CompilesTestresult.objects.filter(testcase__assignment_id=assignment_id,
                                                                      testcase__in=compiles_test_cases,
                                                                      timestamp=ts)

            if compiles_test_results.exists():
                result[ts]['compiles'] = {}
                for ctr in compiles_test_results:
                    result[ts]['compiles'][ctr.solution] = ctr

            contains_test_cases = ContainsTestcase.objects.filter(assignment_id=assignment_id)
            contains_test_results = ContainsTestresult.objects.filter(testcase__assignment_id=assignment_id,
                                                                      testcase__in=contains_test_cases,
                                                                      timestamp=ts)

            if contains_test_results.exists():
                result[ts]['contains'] = {}
                for ctr in contains_test_results:
                    ctc = ContainsTestcase.objects.get(id=ctr.testcase_id)
                    if ctc not in result[ts]['contains']:
                        result[ts]['contains'][ctc] = {}
                    result[ts]['contains'][ctc][ctr.solution] = ctr

            unit_test_cases = UnitTestcase.objects.filter(assignment_id=assignment_id)
            unit_test_results = UnitTestresult.objects.filter(testcase__assignment_id=assignment_id,
                                                              testcase__in=unit_test_cases,
                                                              timestamp=ts)

            if unit_test_results.exists():
                result[ts]['unit'] = {}
                for utr in unit_test_results:
                    result[ts]['unit'][utr.solution] = utr

        return result


class TestcaseContainsOverview(ListView):
    model = ContainsTestcase
    template_name = 'testing/contains/testcase_contains_overview.html'

    def get_queryset(self):
        assignment_pk = self.kwargs.get('ass')
        return ContainsTestcase.objects.filter(assignment_id=assignment_pk).order_by('phrase').all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)

        assignment_pk = self.kwargs.get('ass')
        context['assignment_pk'] = assignment_pk

        return context


class TestcaseContainsAddNew(FormView):
    template_name = 'testing/contains/testcase_contains_add.html'
    form_class = ContainsTestcaseCreateForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assignment = Assignment.objects.get(id=self.kwargs.get('ass'))
        context['assignment'] = assignment

        return context

    def form_valid(self, form):
        new_testcase = ContainsTestcase(assignment_id=self.kwargs.get('ass'),
                                        phrase=form.cleaned_data['phrase'],
                                        times=form.cleaned_data['times'])
        new_testcase.save()

        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'testing-contains-overview',
            kwargs={
                'ass': self.kwargs.get('ass')
            }
        )


class TestcaseContainsDelete(DeleteView):
    model = ContainsTestcase
    context_object_name = 'ctc'
    template_name = 'testing/contains/testcase_contains_delete.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assignment'] = Assignment.objects.get(pk=self.kwargs.get('ass'))
        context['ctc'] = ContainsTestcase.objects.get(pk=self.kwargs.get('pk'))

        return context

    def get_success_url(self):
        return reverse(
            'testing-contains-overview',
            kwargs={
                'ass': self.kwargs.get('ass')
            }
        )


def start_tests_for_assignment(request, ass):
    TestingExecutionThread(assignment_id=ass).start()
    return HttpResponse('')
