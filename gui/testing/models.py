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

    class Meta:
        db_table = "testcase"


class CompilesTestcase(Testcase):
    active = models.BooleanField(blank=True)
    testresults = models.ManyToManyField(Solution, through='CompilesTestresult')

    class Meta:
        db_table = "compiles_testcase"


class ContainsTestcase(Testcase):
    phrase = models.CharField(max_length=64)
    times = models.IntegerField(default=1, blank=True)
    testresults = models.ManyToManyField(Solution, through='ContainsTestresult')

    class Meta:
        db_table = "contains_testcase"

    def __str__(self):
        return self.phrase + ' (' + str(self.times) + 'x)'


class UnitTestcase(Testcase):
    file = models.FileField(upload_to='data/', blank=True)
    testresults = models.ManyToManyField(Solution, through='UnitTestresult')

    class Meta:
        db_table = "unit_testcase"


class CompilesTestresult(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    testcase = models.ForeignKey(CompilesTestcase, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    result = models.BooleanField(blank=True)
    message = models.CharField(max_length=1024, default=' ')

    class Meta:
        db_table = "compiles_testresult"


class ContainsTestresult(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    testcase = models.ForeignKey(ContainsTestcase, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    result = models.BooleanField(blank=True)
    count_wanted = models.IntegerField(blank=True)
    count_found = models.IntegerField(blank=True)

    class Meta:
        db_table = "contains_testresult"


class UnitTestresult(models.Model):
    solution = models.ForeignKey(Solution, on_delete=models.CASCADE)
    testcase = models.ForeignKey(UnitTestcase, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(blank=True)
    result = models.BooleanField(blank=True)
    total_testcases = models.IntegerField()
    success_testcases = models.IntegerField()
    message = models.CharField(max_length=8196, default=' ')

    class Meta:
        db_table = "unit_testresult"
