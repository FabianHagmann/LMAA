from gui.testing.models import UnitTestresult, ContainsTestresult, CompilesTestresult


class UnweightedTestResult:

    def __init__(self, success: bool) -> None:
        """
        Creates a test result for use in compiles test success rate calculation
        :param success: True if success, otherwise false
        """
        self.success = success

    @staticmethod
    def fromCompilesTestresults(testresults: list[CompilesTestresult]):
        """
        Converts a list of compiles testresults into a list of unweighted testresults
        :param testresults: list of compiles testresults
        :return: list of unweighted testresults
        """

        result_list = []
        for single_testresult in testresults:
            result_list.append(UnweightedTestResult(success=single_testresult.result))
        return result_list


class WeightedExpectationTestResult:

    def __init__(self, expectation: int, reality: int) -> None:
        """
        Creates a test result for use in contains and unit test success rate calculation
        :param expectation: expected value
        :param reality: found/success value
        """
        self.expectation = expectation
        self.reality = reality

    @staticmethod
    def fromUnitTestresults(testresults: list[UnitTestresult]):
        """
        Converts a list of unit testresults into a list of weighted expectation testresults
        :param testresults: list of unit testresults
        :return: list of weighted expectation testresults
        """
        result_list = []
        for single_testresult in testresults:
            result_list.append(WeightedExpectationTestResult(expectation=single_testresult.total_testcases,
                                                             reality=single_testresult.success_testcases))
        return result_list

    @staticmethod
    def fromContainsTestresult(testresults: list[ContainsTestresult]):
        """
        Converts a list of contains testresults into a list of weighted expectation testresults
        :param testresults: list of contains testresults
        :return: list of weighted expectation testresults
        """
        result_list = []
        for single_testresult in testresults:
            result_list.append(WeightedExpectationTestResult(expectation=single_testresult.count_wanted,
                                                             reality=single_testresult.count_found))
        return result_list


class SuccessMetric:

    def calculate_success_rate_compiles_multiple(self, testresults_2dim) -> float:
        """
        calculates a single average success rate for compiles testresults of a 2 dim list
        :param testresults_2dim: list of testresults 2dim
        :return: compiles success rate as a float [0;1]
        """
        average_success_list = self.__calculate_unweighted_average_list_multiple_solutions__(testresults_2dim)

        average_success_sum = 0
        for success_rate in average_success_list:
            average_success_sum += success_rate

        return average_success_sum / len(average_success_list)

    def __calculate_unweighted_average_list_multiple_solutions__(self, testresults_2dim) -> [float]:
        """
        calculates a list of unweighted averages from the given 2dim list of testresults
        :param testresults_2dim: list of testcases 2dim
        :return: list of unweighted averages for every set of testresults
        """
        average_success_list = []
        for test_results_for_single_solution in testresults_2dim:
            average_success_list.append(
                self.__calculate_unweighted_average_single_solution__(test_results_for_single_solution))

        return average_success_list

    def __calculate_unweighted_average_single_solution__(self, testresults: list[UnweightedTestResult]) -> float:
        """
        calculates the unweighted average of the given testresults
        :param testresults: given testcases to calculate the success rate for
        :return: unweighted average as a float [0;1]
        """

        average_success = 0

        for testresult in testresults:
            average_success += (1 if testresult.success > 0 else 0)

        return average_success / len(testresults)
