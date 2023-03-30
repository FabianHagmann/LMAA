from datetime import timedelta

from django.shortcuts import render
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.views.generic import FormView

from gui.assignments.models import Assignment, Solution
from gui.communication.forms import LanguageModelRequestForm, LanguageModelRequestConfigurationForm, \
    LanguageModelRequestSolutionEditForm
from gui.communication.models import Property, SolutionRequest, SolutionRequestParameter, \
    SolutionRequestStatus, PropertyType
from gui.communication.tasks import SolutionRequestThread
from scripts.communication import communication_manager as manager


class LanguageModelRequestFormView(FormView):
    """
    FormView for displaying basic solution-request parameters (Assignments [multiselect], Model [singleselect])

    Results are stores as SolutionRequest with status=1 (not_ready = default).
    Success redirect to Configuration-View
    """

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
    """
    FormView view for inputting the requested models parameters dynamically.

    Updates the existing solution request with the entered data and updates the status to 2 (ready).
    Starts a SolutionRequestThread with the resulting SolutionRequest.
    Success redirect to static SuccessPage
    """

    form_class = LanguageModelRequestConfigurationForm
    template_name = 'communication/communication_configure.html'
    success_url = '/communication/new/success'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.communicator = None

    def form_valid(self, form, *args, **kwargs):
        request_pk = self.get_form_kwargs().get('req')
        solution_request = SolutionRequest.objects.get(pk=request_pk)
        params = self.__evaluate_configuration_parameters__(solution_request.model, form)

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
        communication_manager = manager.CommunicatorManager()
        request = SolutionRequest.objects.get(pk=kwargs['req'])
        for communicator in communication_manager.get_implementations():
            if communicator.name != request.model.name:
                continue
            self.communicator = communicator

        kwargs.__setitem__('select_options', self.__get_select_property_options(kwargs.get('req')))
        return kwargs

    def __get_select_property_options(self, solution_request_pk) -> dict[str, tuple[tuple[int, str]]]:
        """
        Get the options provided by the communicator implementation for select-properties

        :param solution_request_pk: key of the current solution_request
        :return: options for all select properties in the style:
            {
                'prop1_options': (
                    (1, 'opt1'),
                    (2, 'opt2')
                )
                'prop2_options':  (
                    (1, 'opt1'),
                    (2, 'opt2')
                )
                ...
            }
        """

        request = SolutionRequest.objects.get(pk=solution_request_pk)
        if request:
            options_for_all_props = {}
            for prop in Property.objects.filter(
                    language_model=SolutionRequest.objects.get(pk=solution_request_pk).model,
                    type=PropertyType.select):
                prop_options_pair = self.__get_options_from_communicator__(prop.name)
                options_for_all_props.__setitem__(prop_options_pair[0], prop_options_pair[1])
            return options_for_all_props
        return {}

    def __get_options_from_communicator__(self, prop_name: str) -> []:
        """
        get available options for a specififed select property from the communicator
        :param prop_name: name of the requested property
        :return: select options in the style
            'prop1_options': (
                (1, 'opt1'),
                (2, 'opt2')
            )
        """

        return [prop_name + '_options',
                tuple((i, value) for i, value in
                      enumerate(list(self.communicator.get_property_options(prop_name).keys()), start=1))]

    def __evaluate_configuration_parameters__(self, model, form):
        """
        Evaluate the dynamically created LanguageModelRequestConfigurationForm
        :param model: requested language model
        :param form: LanguageModelRequestConfigurationForm with parameters for the requested language model
        :return: list of parameters contained in the form
        """

        params = []
        for prop in Property.objects.filter(language_model__name=model.name):
            if prop.is_configuration:
                if prop.type == PropertyType.select:
                    param = SolutionRequestParameter(key=prop.name,
                                                     value=self.__evaluate_configuration_select_parameter__(prop.name,
                                                                                                            form.cleaned_data[
                                                                                                                prop.name]))
                    params.append(param)
                else:
                    param = SolutionRequestParameter(key=prop.name, value=form.cleaned_data[prop.name])
                    params.append(param)
        return params

    def __evaluate_configuration_select_parameter__(self, prop_name, selected_index) -> str:
        """
        evaluate the selected options of a specified select-property
        :param prop_name: name of the requested select-property
        :param selected_index: selected value from the form
        :return: text of the selected option
        """
        return list(self.communicator.get_property_options(prop_name).items())[int(selected_index) - 1][1]


def communication_success_view(request):
    """
    Static success page for confirming the started SolutionRequestThread
    """
    return render(request, 'communication/communication_success.html', context={})


class LanguageModelRequestSolutionEditFormView(FormView):
    """
    FormView for displaying the current state of created Solutionrequests.
    Displays:
    - currently running solutionrequests
    - recently failed solutionrequests
    - newly generated solutions (for edit by the user)
    """

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
