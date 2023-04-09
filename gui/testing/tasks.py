import threading

from gui.assignments.models import Assignment, Solution
from gui.testing.models import CompilesTestcase, ContainsTestcase, UnitTestcase, Testcase, Testresult

from scripts.testing import testing_manager as manager
from scripts.testing.testing_executors import TestExecutionResponse


class TestingExecutionThread(threading.Thread):

    def __init__(self, assignment_id: int, **kwargs) -> None:
        self.assignment_id = assignment_id
        super(TestingExecutionThread, self).__init__(**kwargs)

    def run(self) -> None:
        # fetch and check assignment
        try:
            assignment = Assignment.objects.get(id=self.assignment_id)
        except Exception:
            # TODO
            return

        # fetch all testcases for assignment
        check_compile = CompilesTestcase.objects.filter(assignment=assignment, active=True).get()
        contains_testcases = ContainsTestcase.objects.filter(assignment=assignment).all()
        unit_testcase = UnitTestcase.objects.filter(assignment=assignment).all()

        # execute testcases
        man = manager.TestingManager()

        # for every solution available for the assignment
        for solution in Solution.objects.filter(assignment=assignment).all():
            if check_compile:
                response = man.solution_compiles(solution.solution)
                self.__store_execution_response__(response, solution, check_compile)

            for ctc in contains_testcases:
                response = man.solution_contains(solution.solution, ctc.phrase, ctc.times)
                self.__store_execution_response__(response, solution, ctc)

    #         TODO: unit test execution

    def __store_execution_response__(self, response: TestExecutionResponse, solution: Solution, testcase: Testcase):
        test_result = Testresult(timestamp=response.timestamp,
                                result=response.result,
                                message=response.message,
                                solution=solution,
                                testcase=testcase)
        test_result.save()
