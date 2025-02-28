from scripts.testing.testing_executors import CompileTestExecutor, ContainsTestExecutor, UnitTestExecutor, \
    TestExecutionCompilesResponse, TestExecutionContainsResponse, TestExecutionUnitResponse


class TestingManager:
    """
    Manager for accessing all test-executors from a single source

    This is the only testing-class accessed by the frontend
    """

    def __init__(self) -> None:
        self.__compile_executor__ = CompileTestExecutor()
        self.__contains_executor__ = ContainsTestExecutor()
        self.__unit_executor__ = UnitTestExecutor()

    def solution_contains(self, solution: str, phrase: str, times: int) -> TestExecutionContainsResponse:
        """
        checks if a given solutions contains a phrase n times

        :param solution: given solution to be checked
        :param phrase: phrase that is checks to be contained
        :param times: number of times the phrase has to be contained
        :return: TestExecutionContainsResponse containing the result
        """
        return self.__contains_executor__.execute_test(solution, phrase, times)

    def solution_compiles(self, solution: str) -> TestExecutionCompilesResponse:
        """
        checks if a given solution compiles as java code

        :param solution: given solution to be checked
        :return: TestExecutionResponse containing the result
        """
        return self.__compile_executor__.execute_test(solution)

    def solution_unit_test(self, solution: str, unit_test: str) -> TestExecutionUnitResponse:
        """
        checks if a given solution passes a given unit test

        :param solution: given solution to be checked
        :param unit_test: given unit test to be executed on the solution
        :return: TestExecutionResponse containing the result
        """
        return self.__unit_executor__.execute_test(solution, unit_test)
