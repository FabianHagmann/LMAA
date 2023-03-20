from enum import IntEnum

from django.db import models


class PropertyType(IntEnum):
    int = 1
    float = 2
    str = 3

    @classmethod
    def choices(cls):
        return [(key.value, key.name) for key in cls]


class LanguageModel(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "llm"

    def __str__(self):
        return self.name


class Property(models.Model):
    name = models.CharField(max_length=64)
    type = models.IntegerField(choices=PropertyType.choices(), default=PropertyType.float)
    mandatory = models.BooleanField()
    language_model = models.ForeignKey(LanguageModel, on_delete=models.CASCADE)

    class Meta:
        db_table = "llm_property"

    def __str__(self):
        return self.name
