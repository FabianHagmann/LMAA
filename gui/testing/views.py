from django.urls import reverse
from django.views.generic import TemplateView, FormView, ListView, DeleteView

from gui.assignments.models import Assignment
from gui.testing.forms import AssignmentTestcasesForm, ContainsTestcaseCreateForm
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

        assignment_pk = self.kwargs['ass']
        self.assignment = Assignment.objects.get(pk=assignment_pk)
        kwargs.__setitem__('ass', assignment_pk)

        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['assignment_pk'] = self.kwargs.get('ass')
        context['containsTestcases'] = ContainsTestcase.objects.filter(assignment_id=self.kwargs['ass']) \
            .order_by('phrase').all()

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


