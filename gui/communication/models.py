import json
import threading
from enum import IntEnum

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.datetime_safe import datetime

from gui.assignments.models import Assignment, Solution
from scripts.communication import communication_manager as manager


class PropertyType(IntEnum):
    int = 1
    float = 2
    str = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class SolutionRequestStatus(IntEnum):
    not_ready = 1
    ready = 2
    running = 3
    completed = 4
    failed = 5

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class LanguageModel(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "llm"

    def __str__(self):
        return self.name

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Property(models.Model):
    name = models.CharField(max_length=64)
    type = models.IntegerField(choices=PropertyType.choices(), default=PropertyType.float)
    mandatory = models.BooleanField()
    default = models.CharField(max_length=64, default="")
    is_configuration = models.BooleanField(default=False)
    language_model = models.ForeignKey(LanguageModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "llm_property"

    def __str__(self):
        return self.name

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class SolutionRequestParameter(models.Model):
    key = models.CharField(max_length=64)
    value = models.CharField(max_length=64)

    class Meta:
        db_table = "solution_request_parameter"


class SolutionRequest(models.Model):
    assignments = models.ManyToManyField(Assignment)
    model = models.ForeignKey(LanguageModel, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    parameters = models.ManyToManyField(SolutionRequestParameter)
    status = models.IntegerField(choices=SolutionRequestStatus.choices(), default=SolutionRequestStatus.not_ready)
    repeats = models.IntegerField(default=1,
                                  validators=[
                                      MaxValueValidator(5),
                                      MinValueValidator(1)
                                  ])

    class Meta:
        db_table = "solution_request"


class SolutionRequestThread(threading.Thread):

    def __init__(self, instance: SolutionRequest, **kwargs):
        self.instance = instance
        super(SolutionRequestThread, self).__init__(**kwargs)

    def run(self) -> None:
        # only send "ready" requests
        if self.instance.status != SolutionRequestStatus.ready:
            return

        self.instance.status = SolutionRequestStatus.running
        self.instance.save()

        # get selected communicator
        man = manager.CommunicatorManager()
        selected_communicator = None
        for communicator in man.get_implementations():
            if communicator.name == self.instance.model.name:
                selected_communicator = communicator

        # handle selected communicator not found
        if selected_communicator is None:
            self.instance.status = SolutionRequestStatus.failed
            self.instance.save()
            return

        # add solution_request parameters to properties list
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

        # send request for every assignment in solution_request
        for ass in self.instance.assignments.all():
            for i in range(self.instance.repeats):
                request_parameters.__setitem__('prompt', ass.assignment)
                communication_response = selected_communicator.send_request(request_parameters=request_parameters)
                if communication_response.code == 200:
                    sol = Solution(timestamp=datetime.now(), communicator=self.instance.model.name,
                                   solution=communication_response.payload,
                                   assignment=ass, is_new=True)
                    sol.save()
                else:
                    self.instance.status = SolutionRequestStatus.failed
                    self.instance.save()
                    return

        self.instance.status = SolutionRequestStatus.completed
        self.instance.save()
