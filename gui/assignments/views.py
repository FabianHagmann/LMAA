from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DeleteView

from gui.assignments.forms import AssignmentsForm, TagsForm
from gui.assignments.models import Assignment, Tag


class AssignmentsList(ListView):
    model = Assignment
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class AssignmentsView(AssignmentsList):
    template_name = 'assignments/assignment_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def create_assignment(request):
    form = AssignmentsForm()
    if request.method == 'POST':
        form = AssignmentsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments')
    context = {'form': form, 'is_update': False, 'is_disabled': False}
    return render(request, 'assignments/assignments_form.html', context)


def edit_assignment(request, pk):
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
    model = Assignment
    context_object_name = 'assignment'
    success_url = reverse_lazy('assignments')
    template_name = 'assignments/assignments_confirm_delete.html'


class TagList(ListView):
    model = Tag
    queryset = Tag.objects.order_by('name')


class TagView(TagList):
    template_name = 'assignments/tags/tag_main.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


def create_tag(request):
    form = TagsForm()
    if request.method == 'POST':
        form = TagsForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/assignments/tags')
    context = {'form': form, 'is_update': False}
    return render(request, 'assignments/tags/tag_form.html', context)


def edit_tag(request, pk):
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
    model = Tag
    context_object_name = 'tag'
    success_url = reverse_lazy('tags')
    template_name = 'assignments/tags/tag_confirm_delete.html'
