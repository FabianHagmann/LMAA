from django import forms
from django.utils.datetime_safe import datetime
from django.views.generic import FormView

from gui.assignments.models import Assignment, Solution
from gui.communication.forms import LanguageModelRequestForm, LanguageModelRequestConfigurationForm, \
    LanguageModelRequestSolutionEditForm
from gui.communication.models import Property, PropertyType, SolutionRequest, SolutionRequestParameter, \
    SolutionRequestStatus
from scripts.communication import communication_manager as manager


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
    success_url = '/communication/new/edit'

    def form_valid(self, form):
        solution_request = SolutionRequest.objects.order_by('timestamp').first()
        params = __evaluate_configuration_form__(solution_request.model, form)
        for param in params:
            param.save()
            solution_request.parameters.add(param)
        solution_request.status = SolutionRequestStatus.ready
        solution_request.save()

        __queue_solution_request__(solution_request)

        return super().form_valid(form)


class LanguageModelRequestSolutionEditFormView(FormView):
    form_class = LanguageModelRequestSolutionEditForm
    template_name = 'communication/communication_edit_response.html'
    success_url = '/communication/new'

    def form_invalid(self, form):
        print('I am invalid')
        return super().form_invalid(form)

    def form_valid(self, form):
        for field in form.fields:
            sol = Solution.objects.get(pk=int(field.__str__()[3:]))
            sol.is_new = False
            sol.solution = form.cleaned_data[field]
            sol.save()

        return super().form_valid(form)


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


def __queue_solution_request__(instance: SolutionRequest):
    # get selected communicator
    man = manager.CommunicatorManager()
    selected_communicator = None
    for communicator in man.get_implementations():
        if communicator.name == instance.model.name:
            selected_communicator = communicator

    if selected_communicator is None:
        print("Error executing scheduled solution_request: model not found")
        # todo: delete solution_request

    # add solution_request parameters to properties list
    request_parameters = {}
    for prop in Property.objects.filter(language_model=instance.model):
        for param in instance.parameters.all():
            if prop.name == param.key:
                match prop.type:
                    case 1:
                        request_parameters.__setitem__(param.key, int(param.value))
                    case 2:
                        request_parameters.__setitem__(param.key, float(param.value))
                    case _:
                        request_parameters.__setitem__(param.key, param.value)
                continue

    # send request for every assignment in solution_request
    for ass in instance.assignments.all():
        request_parameters.__setitem__('prompt', ass.assignment)
        communication_response = selected_communicator.send_request(request_parameters=request_parameters)
        if communication_response.code == 200:
            sol = Solution(timestamp=datetime.now(), communicator=instance.model.name,
                           solution=communication_response.payload,
                           assignment=ass, is_new=True)
            sol.save()
        # else:
        # todo: handle error

    instance.delete()
