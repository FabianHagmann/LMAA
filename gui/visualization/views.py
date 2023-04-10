from django.http import JsonResponse
from django.views.generic import TemplateView

from gui.assignments.models import Assignment, Solution


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

        return context


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
