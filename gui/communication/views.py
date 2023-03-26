from datetime import timedelta

from django import forms
from django.shortcuts import render
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.views.generic import FormView

from gui.assignments.models import Assignment, Solution
from gui.communication.forms import LanguageModelRequestForm, LanguageModelRequestConfigurationForm, \
    LanguageModelRequestSolutionEditForm
from gui.communication.models import Property, PropertyType, SolutionRequest, SolutionRequestParameter, \
    SolutionRequestStatus, SolutionRequestThread


class LanguageModelRequestFormView(FormView):
    template_name = 'communication/communication_select.html'
    form_class = LanguageModelRequestForm

    def __init__(self, **kwargs):
        super(FormView, self).__init__(**kwargs)
        self.success_pk = None

    def form_valid(self, form):
        model = form.cleaned_data['models']
        solution_request = SolutionRequest(model=model)
        solution_request.save()

        for ass in form.cleaned_data['assignments']:
            solution_request.assignments.add(Assignment.objects.get(id=ass.id))
        solution_request.save()
        self.success_pk = solution_request.id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'communication-configure',
            kwargs={
                'req': self.success_pk
            }
        )


class LanguageModelRequestConfigurationFormView(FormView):
    form_class = LanguageModelRequestConfigurationForm
    template_name = 'communication/communication_configure.html'
    success_url = '/communication/new/success'

    def form_valid(self, form, *args, **kwargs):
        request_pk = self.get_form_kwargs().get('req')
        print(request_pk)
        solution_request = SolutionRequest.objects.get(pk=request_pk)
        params = __evaluate_configuration_parameters__(solution_request.model, form)
        for param in params:
            param.save()
            solution_request.parameters.add(param)

        solution_request.repeats = form.cleaned_data['repeats']
        solution_request.status = SolutionRequestStatus.ready
        solution_request.save()

        solution_request = SolutionRequest.objects.get(pk=solution_request.pk)
        SolutionRequestThread(solution_request).start()

        return super().form_valid(form)

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(LanguageModelRequestConfigurationFormView, self).get_form_kwargs()
        kwargs.__setitem__('req', self.kwargs['req'])
        return kwargs


def communication_success_view(request):
    return render(request, 'communication/communication_success.html', context={})


class LanguageModelRequestSolutionEditFormView(FormView):
    form_class = LanguageModelRequestSolutionEditForm
    template_name = 'communication/communication_edit_response.html'
    success_url = '/communication/status'

    def form_valid(self, form):
        for field in form.fields:
            sol = Solution.objects.get(pk=int(field.__str__()[3:]))
            sol.is_new = False
            sol.solution = form.cleaned_data[field]
            sol.save()

        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        running_requests = SolutionRequest.objects.filter(status=SolutionRequestStatus.running).all()
        context["running_requests"] = running_requests

        recent_time_window = datetime.now() - timedelta(hours=3)
        recently_failed_requests = SolutionRequest.objects.filter(status=SolutionRequestStatus.failed,
                                                                  timestamp__gte=recent_time_window).all()
        context["recently_failed"] = recently_failed_requests

        return context


def __evaluate_configuration_parameters__(model, form):
    params = []
    for prop in Property.objects.filter(language_model__name=model.name):
        if prop.is_configuration:
            param = SolutionRequestParameter(key=prop.name, value=form.cleaned_data[prop.name])
            params.append(param)
    return params


def __build_configure_form__(model, is_get):
    if is_get:
        form = forms.Form()
    else:
        form = forms.Form('POST')

    if model is None:
        return form

    for prop in Property.objects.filter(language_model__name=model.name):
        if prop.is_configuration:
            if prop.type == PropertyType.int:
                form.fields[prop.name] = forms.IntegerField(required=prop.mandatory, initial=int(prop.default))
            elif prop.type == PropertyType.float:
                form.fields[prop.name] = forms.FloatField(required=prop.mandatory, initial=float(prop.default))
            else:
                form.fields[prop.name] = forms.CharField(required=prop.mandatory, initial=prop.default)

    return form
