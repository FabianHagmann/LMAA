from django.db import models

from gui.assignments.models import Assignment, Solution

"""
Contains all models required for assignments-pages
<ul>
    <li>Testcase</li>
    <li>CompilesTestcase</li>
    <li>ContainsTestcase</li>
    <li>UnitTestcase</li>
    <li>CompilesTestresult</li>
    <li>ContainsTestresult</li>
    <li>UnitTestresult</li>
</ul>

Additional non-model classes
<ul>
    <li>AssignmentWithTestcases</li>
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


# Additional non-model classes
class AssignmentWithTestcases:
    """
    Additional class to store an assignment in combination with
        - the status of the compiles testcase
        - the number of contains testcases
        - the status of the unit testcase
    """
    def __init__(self, assignment: Assignment = None, compiles_testcase_active: bool = False,
                 contains_testcases: int = 0, unit_testcase_active: bool = False) -> None:
        """
        init method
        :param assignment: assignment in question
        :param compiles_testcase_active: status of the compiles testcase
        :param contains_testcases: number of contains testcases
        :param unit_testcase_active: status of the unit testcase
        """
        self.assignment = assignment
        self.compiles_testcase = compiles_testcase_active
        self.contains_testcases = contains_testcases
        self.unit_testcase = unit_testcase_active
        super().__init__()