import threading

from django.utils.datetime_safe import datetime

from gui.assignments.models import Assignment, Solution
from gui.testing.models import CompilesTestcase, ContainsTestcase, UnitTestcase, Testcase, Testresult
from scripts.testing import testing_manager as manager
from scripts.testing.testing_executors import TestExecutionResponse


class TestingExecutionThread(threading.Thread):

    def __init__(self, assignment_id: int, **kwargs) -> None:
        self.assignment_id = assignment_id
        super(TestingExecutionThread, self).__init__(**kwargs)

    def run(self) -> None:
        execution_timestamp = datetime.now()

        # fetch and check assignment
        try:
            assignment = Assignment.objects.get(id=self.assignment_id)
        except Assignment.DoesNotExist:
            # TODO
            return

        # fetch all testcases for assignment
        try:
            check_compile = CompilesTestcase.objects.filter(assignment=assignment, active=True).get()
        except CompilesTestcase.DoesNotExist:
            check_compile = None

        contains_testcases = ContainsTestcase.objects.filter(assignment=assignment).all()
        try:
            unit_testcase = UnitTestcase.objects.filter(assignment=assignment).get()
        except UnitTestcase.DoesNotExist:
            unit_testcase = None

        # execute testcases
        man = manager.TestingManager()

        # for every solution available for the assignment
        for solution in Solution.objects.filter(assignment=assignment).all():
            if check_compile is not None:
                response = man.solution_compiles(solution.solution)
                self.__store_execution_response__(response, solution, check_compile, execution_timestamp)

            for ctc in contains_testcases:
                response = man.solution_contains(solution.solution, ctc.phrase, ctc.times)
                self.__store_execution_response__(response, solution, ctc, execution_timestamp)

            if unit_testcase is not None:
                unit_test_code = self.__convert_file_to_string__(unit_testcase.file)
                response = man.solution_unit_test(solution.solution, unit_test_code)
                self.__store_execution_response__(response, solution, unit_testcase, execution_timestamp)

    def __store_execution_response__(self, response: TestExecutionResponse, solution: Solution, testcase: Testcase,
                                     timestamp):
        test_result = Testresult(timestamp=timestamp,
                                 result=response.result,
                                 message=response.message,
                                 solution=solution,
                                 testcase=testcase)
        test_result.save()

    def __convert_file_to_string__(self, file) -> str:
        code = ''
        file_stream = file.open(mode='rb')

        for line in file_stream:
            code += line.decode('utf-8')
        return code
