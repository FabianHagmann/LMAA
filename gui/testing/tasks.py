import threading

from django.utils.datetime_safe import datetime

from gui.assignments.models import Assignment, Solution
from gui.testing.models import CompilesTestcase, ContainsTestcase, UnitTestcase, Testcase, CompilesTestresult, \
    ContainsTestresult, UnitTestresult
from scripts.testing import testing_manager as manager
from scripts.testing.testing_executors import TestExecutionCompilesResponse, TestExecutionContainsResponse, \
    TestExecutionUnitResponse


class TestingExecutionThread(threading.Thread):
    """
    Thread for asynchronously executing assignment tests

    Receives an assignment id and executes all available testcases for the selected assignment
    Stores the generated testresults in the database
    """

    def __init__(self, assignment_id: int, **kwargs) -> None:
        self.assignment_id = assignment_id
        super(TestingExecutionThread, self).__init__(**kwargs)

    def run(self) -> None:
        """
        fetch the assignment and its testcases and execute them
        """

        execution_timestamp = datetime.now()

        # fetch and check assignment
        try:
            assignment = Assignment.objects.get(id=self.assignment_id)
        except Assignment.DoesNotExist:
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
                self.__store_execution_compile_response__(response, solution, check_compile, execution_timestamp)

            for ctc in contains_testcases:
                response = man.solution_contains(solution.solution, ctc.phrase, ctc.times)
                self.__store_execution_contains_response__(response, solution, ctc, execution_timestamp)

            if unit_testcase is not None:
                unit_test_code = self.__convert_file_to_string__(unit_testcase.file)
                response = man.solution_unit_test(solution.solution, unit_test_code)
                self.__store_execution_unit_response__(response, solution, unit_testcase, execution_timestamp)

    def __store_execution_compile_response__(self, response: TestExecutionCompilesResponse, solution: Solution,
                                             testcase: CompilesTestcase,
                                             timestamp):
        """
        stores the testresult from an execution
        :param response: execution response
        :param solution: solution of the response
        :param testcase: testcase of the response
        :param timestamp: execution timestamp
        """

        compile_test_result = CompilesTestresult(solution=solution,
                                                 testcase=testcase,
                                                 timestamp=timestamp,
                                                 result=response.result,
                                                 message=response.message)
        compile_test_result.save()

    def __store_execution_contains_response__(self, response: TestExecutionContainsResponse, solution: Solution,
                                              testcase: ContainsTestcase,
                                              timestamp):
        """
        stores the testresult from an execution
        :param response: execution response
        :param solution: solution of the response
        :param testcase: testcase of the response
        :param timestamp: execution timestamp
        """

        contains_test_result = ContainsTestresult(solution=solution,
                                                  testcase=testcase,
                                                  timestamp=timestamp,
                                                  result=response.get_result(),
                                                  count_found=response.found,
                                                  count_wanted=response.wanted)
        contains_test_result.save()

    def __store_execution_unit_response__(self, response: TestExecutionUnitResponse, solution: Solution,
                                              testcase: UnitTestcase,
                                              timestamp):
        """
        stores the testresult from an execution
        :param response: execution response
        :param solution: solution of the response
        :param testcase: testcase of the response
        :param timestamp: execution timestamp
        """

        unit_test_result = UnitTestresult(solution=solution,
                                          testcase=testcase,
                                          timestamp=timestamp,
                                          result=response.get_result(),
                                          total_testcases=response.total_testcases,
                                          success_testcases=response.success_testcases,
                                          message=response.message)
        unit_test_result.save()

    def __convert_file_to_string__(self, file) -> str:
        """
        converts the uploaded unit test file into a string to be passed to the test-executor
        :param file: file to be converted
        :return: converted string of unittest-file
        """

        code = ''
        file_stream = file.open(mode='rb')

        for line in file_stream:
            code += line.decode('utf-8')
        return code
