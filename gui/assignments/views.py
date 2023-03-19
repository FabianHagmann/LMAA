from django.utils import timezone
from django.views.generic import ListView

from gui.assignments.models import Assignment


class AssignmentsList(ListView):
    model = Assignment
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


class AssignmentsView(AssignmentsList):
    template_name = 'assignments/assignment_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
