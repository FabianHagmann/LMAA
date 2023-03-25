from django import forms
from django.shortcuts import render
from django.views.generic import FormView

from gui.assignments.models import Assignment, Solution
from gui.communication.forms import LanguageModelRequestForm, LanguageModelRequestConfigurationForm, \
    LanguageModelRequestSolutionEditForm
from gui.communication.models import Property, PropertyType, SolutionRequest, SolutionRequestParameter, \
    SolutionRequestStatus, SolutionRequestThread


class LanguageModelRequestFormView(FormView):
    template_name = 'communication/communication_select.html'
    form_class = LanguageModelRequestForm
    success_url = '/communication/new/configure'

    def form_valid(self, form):
        model = form.cleaned_data['models']
        solution_request = SolutionRequest(model=model)
        solution_request.save()

        solution_request = SolutionRequest.objects.order_by('timestamp').first()
        for ass in form.cleaned_data['assignments']:
            solution_request.assignments.add(Assignment.objects.get(id=ass.id))
        solution_request.save()
        return super().form_valid(form)


class LanguageModelRequestConfigurationFormView(FormView):
    form_class = LanguageModelRequestConfigurationForm
    template_name = 'communication/communication_configure.html'
    success_url = '/communication/new/success'

    def form_valid(self, form):
        solution_request = SolutionRequest.objects.order_by('timestamp').first()
        params = __evaluate_configuration_form__(solution_request.model, form)
        for param in params:
            param.save()
            solution_request.parameters.add(param)
        solution_request.status = SolutionRequestStatus.ready
        solution_request.save()

        # __queue_solution_request__(solution_request)
        solution_request = SolutionRequest.objects.get(pk=solution_request.pk)
        SolutionRequestThread(solution_request).start()

        return super().form_valid(form)


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

        return context


def __evaluate_configuration_form__(model, form):
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
