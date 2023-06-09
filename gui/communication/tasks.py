import threading

from django.utils.datetime_safe import datetime

from gui.assignments.models import Solution
from gui.communication.models import SolutionRequestStatus, SolutionRequest, Property
from scripts.communication import communication_manager as manager


class SolutionRequestThread(threading.Thread):
    """
    Thread for asynchronously executing solution requests

    Receives a solution request, and executes the communication with the requested language model.
    Stores generated solutions in the database.
    Updates SolutionRequest.status according to the results
    """

    def __init__(self, instance: SolutionRequest, **kwargs):
        self.instance = instance
        super(SolutionRequestThread, self).__init__(**kwargs)

    def run(self) -> None:
        # only send "ready" requests
        if self.instance.status != SolutionRequestStatus.ready:
            return

        # if request "ready" set to "running"
        self.instance.status = SolutionRequestStatus.running
        self.instance.save()

        # get selected communicator implementation
        man = manager.CommunicatorManager()
        selected_communicator = None
        for communicator in man.get_implementations():
            if communicator.name == self.instance.model.name:
                selected_communicator = communicator

        # handle selected communicator-not-found
        if selected_communicator is None:
            self.instance.status = SolutionRequestStatus.failed
            self.instance.save()
            return

        # add solution_request parameters to communication-properties list
        request_parameters = {}
        for prop in Property.objects.filter(language_model=self.instance.model):
            for param in self.instance.parameters.all():
                if prop.name == param.key:
                    match prop.type:
                        case 1:
                            request_parameters.__setitem__(param.key, int(param.value))
                        case 2:
                            request_parameters.__setitem__(param.key, float(param.value))
                        case _:
                            request_parameters.__setitem__(param.key, param.value)
                    continue

        # send request for every assignment in solution_request (repeat times)
        for ass in self.instance.assignments.all():
            for i in range(self.instance.repeats):
                request_parameters.__setitem__('prompt', ass.assignment)
                communication_response = selected_communicator.send_request(request_parameters=request_parameters)
                if communication_response.code == 200:
                    solution_text = communication_response.payload
                    if solution_text.startswith('```'):
                        solution_text = solution_text[solution_text.find('\n')+1:len(solution_text)]
                    if solution_text.endswith('```'):
                        solution_text = solution_text[0:solution_text.rfind('```')]

                    sol = Solution(timestamp=datetime.now(), communicator=self.instance.model.name,
                                   solution=solution_text,
                                   assignment=ass, is_new=True)
                    sol.save()
                else:
                    # if request failed, set status and abort
                    self.instance.status = SolutionRequestStatus.failed
                    self.instance.save()
                    return

        # if requests succeeded, set status and finish
        self.instance.status = SolutionRequestStatus.completed
        self.instance.save()
