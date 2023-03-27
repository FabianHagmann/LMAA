from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DeleteView

from gui.assignments.forms import AssignmentsForm, TagsForm
from gui.assignments.models import Assignment, Tag


class AssignmentsList(ListView):
    """
    Paginated ListView for displaying assignments. Displays assignments ordered by semester-sheet-task-subtask at a
    pagination size of 10
    """

    model = Assignment
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AssignmentsView(AssignmentsList):
    """
    Overview view for assignments. Displays AssignmentsList and options for manipulating assignments and tags
    """

    template_name = 'assignments/assignment_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def create_assignment(request):
    """
    View for creating assignments. Renders AssignmentsForm for new entries
    """

    form = AssignmentsForm()
    if request.method == 'POST':
        form = AssignmentsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments')
    context = {'form': form, 'is_update': False, 'is_disabled': False}
    return render(request, 'assignments/assignments_form.html', context)


def edit_assignment(request, pk):
    """
    View for updating assignments. Renders AssignmentsForm for existing entries
    :param pk: primary key of the currently edited assignment
    """

    assignment = Assignment.objects.get(id=pk)
    if request.method == 'POST':
        form = AssignmentsForm(request.POST, instance=assignment)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments')
    else:
        form = AssignmentsForm(instance=assignment)

    return render(request, 'assignments/assignments_form.html', {'id': pk, 'form': form, 'is_update': True,
                                                                 'is_disabled': False})


def assignment_details(request, pk):
    """
    View for viewing assignment details. Renders AssignmentsForm, as a disabled form, for existing entries
    :param pk: primary key of the currently edited assignment
    """

    assignment = Assignment.objects.get(id=pk)
    if request.method == 'POST':
        form = AssignmentsForm(request.POST, instance=assignment)
        form.fields['semester'].disabled = True
        form.fields['sheet'].disabled = True
        form.fields['task'].disabled = True
        form.fields['subtask'].disabled = True
        form.fields['assignment'].disabled = True
        form.fields['effort'].disabled = True
        form.fields['scope'].disabled = True
        form.fields['tags'].disabled = True

        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments')
    else:
        form = AssignmentsForm(instance=assignment)
        form.fields['semester'].disabled = True
        form.fields['sheet'].disabled = True
        form.fields['task'].disabled = True
        form.fields['subtask'].disabled = True
        form.fields['assignment'].disabled = True
        form.fields['effort'].disabled = True
        form.fields['scope'].disabled = True
        form.fields['tags'].disabled = True

    return render(request, 'assignments/assignments_form.html', {'id': pk, 'form': form, 'is_update': False,
                                                                 'is_disabled': True})


class AssignmentsDelete(DeleteView):
    """
    Renders a DeleteView for assignments
    """

    model = Assignment
    context_object_name = 'assignment'
    success_url = reverse_lazy('assignments')
    template_name = 'assignments/assignments_confirm_delete.html'


class TagList(ListView):
    """
    View for displaying all existing tags
    """

    model = Tag
    queryset = Tag.objects.order_by('name')


class TagView(TagList):
    """
    View for displaying the TagList and options for manipulating and managing tags.
    """

    template_name = 'assignments/tags/tag_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def create_tag(request):
    """
    View for creating tags. Renders TagsForm for new entries
    """

    form = TagsForm()
    if request.method == 'POST':
        form = TagsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments/tags')
    context = {'form': form, 'is_update': False}
    return render(request, 'assignments/tags/tag_form.html', context)


def edit_tag(request, pk):
    """
    View for updating tags. Renders TagsForm for existing entries
    """

    tag = Tag.objects.get(id=pk)
    if request.method == 'POST':
        form = TagsForm(request.POST, instance=tag)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments/tags')
    else:
        form = TagsForm(instance=tag)

    return render(request, 'assignments/tags/tag_form.html', {'id': pk, 'form': form, 'is_update': True})


class TagsDelete(DeleteView):
    """
    Renders a DeleteView for tags
    """

    model = Tag
    context_object_name = 'tag'
    success_url = reverse_lazy('tags')
    template_name = 'assignments/tags/tag_confirm_delete.html'
