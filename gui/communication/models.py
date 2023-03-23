import json
from enum import IntEnum

from django.db import models

from gui.assignments.models import Assignment


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

    class Meta:
        db_table = "solution_request"
