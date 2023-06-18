import os

import yaml
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from lmaa.settings import BASE_DIR

config_stream = open(os.path.join(BASE_DIR, 'config', 'system_config.yaml'), 'r')
config_map = yaml.safe_load(config_stream)
assignment_maxlength = config_map['management']['database']['maxlength']['assignment']
solution_maxlength = config_map['management']['database']['maxlength']['solution']

"""
Contains all models required for assignments-pages
<ul>
    <li>Tag</li>
    <li>Assignment</li>
    <li>Solution</li>
</ul>
"""


class Tag(models.Model):
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "tag"

    def __str__(self):
        return self.name


class Assignment(models.Model):
    semester = models.CharField(max_length=6)
    sheet = models.IntegerField()
    task = models.IntegerField()
    subtask = models.CharField(max_length=8, default=None, blank=True, null=True)
    assignment = models.CharField(max_length=assignment_maxlength)
    effort = models.IntegerField(default=None, blank=True, null=True,
                                 validators=[
                                     MaxValueValidator(5),
                                     MinValueValidator(1)
                                 ]
                                 )
    scope = models.IntegerField(default=None, blank=True, null=True,
                                validators=[
                                    MaxValueValidator(5),
                                    MinValueValidator(1)
                                ]
                                )
    tags = models.ManyToManyField(Tag)

    class Meta:
        db_table = "assignment"

    def __str__(self):
        return self.semester + '-AB' + str(self.sheet) + '-' + str(self.task) \
            + (self.subtask if self.subtask is not None else '')


class Solution(models.Model):
    timestamp = models.DateTimeField(blank=True)
    communicator = models.CharField(max_length=64, blank=True)
    solution = models.CharField(max_length=solution_maxlength, blank=True)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    is_new = models.BooleanField(default=False)

    class Meta:
        db_table = "solution"
