from django.views.generic import TemplateView, FormView

from gui.assignments.models import Assignment
from gui.testing.forms import AssignmentTestcasesForm
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
            compiles_testcase_active = CompilesTestcase.objects.filter(assignment=ass, active=True).exists()
            contains_testcases = ContainsTestcase.objects.filter(assignment=ass).count()
            unit_testcase_active = UnitTestcase.objects.filter(assignment=ass).exists()

            assignments.append(
                AssignmentWithTestcases(ass, compiles_testcase_active, contains_testcases, unit_testcase_active))
        return assignments


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

        assignment_pk = self.kwargs['pk']
        self.assignment = Assignment.objects.get(pk=assignment_pk)
        kwargs.__setitem__('ass', assignment_pk)

        return kwargs

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
