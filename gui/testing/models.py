from django.core.validators import MaxValueValidator
from django.db import models

from gui.assignments.models import Assignment, Solution

"""
Contains all models required for assignments-pages
<ul>
    <li>Testcase</li>
    <li>CompilesTestcase</li>
    <li>ContainsTestcase</li>
    <li>UnitTestcase</li>
    <li>Testresult</li>
</ul>
"""


class Testcase(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    testresults = models.ManyToManyField(Solution, through='Testresult')

    class Meta:
        db_table = "testcase"


class CompilesTestcase(Testcase):
    active = models.BooleanField(blank=True)

    class Meta:
        db_table = "compiles_testcase"


class ContainsTestcase(Testcase):
    phrase = models.CharField(max_length=64)
    times = models.IntegerField(default=1, blank=True)

    class Meta:
        db_table = "contains_testcase"


class UnitTestcase(Testcase):
    file = models.FileField(upload_to='db_files/', blank=True)

    class Meta:
        db_table = "unit_testcase"


class Testresult(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    testcase = models.ForeignKey(Testcase, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    result = models.BooleanField(blank=True)
    message = models.CharField(
        validators=[
            MaxValueValidator(1024)
        ]
    ),

    class Meta:
        db_table = "testresult"
