from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.generic import ListView

from gui.assignments.forms import AssignmentsCreateForm
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


def create_assignment(request):
    form = AssignmentsCreateForm
    if request.method == 'POST':
        form = AssignmentsCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments')
    context = {'form': form}
    return render(request, 'assignments/assignments_create_form.html', context)
