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

    def calculate_tag_compiles_success_rate(self, testresults_2dim: list[list[UnweightedTestResult]]) -> float:
        """
        calculates a single average success rate for multiple solutions
        :param testresults_2dim: list of testresults for a tag. the 1st represents the assignments, the 2nd dimension represents the must current testresults for the assignment
        :return: compiles success rate as a float [0;1]
        """
        average_success_list = self.__calculate_unweighted_average_list_multiple_assignments__(testresults_2dim)

        average_success_sum = 0
        for success_rate in average_success_list:
            average_success_sum += success_rate

        return average_success_sum / len(average_success_list)

    def calculate_assignment_compiles_success_rate(self, testresults: list[UnweightedTestResult]) -> float:
        """
        calculates the average compiles success rate for a single assignment
        :param testresults: list of the most current unweighted testresult for all solutions of the assignment
        :return: compiles success rate as a float [0;1]
        """
        return self.__calculate_unweighted_average_single_assignment__(testresults)

    def calculate_assignment_unit_success_rate(self, test_results: list[WeightedExpectationTestResult]) -> float:
        """
        calculates the average unit success rate for a single assignment
        :param test_results: list of the most current weighted unit testresults for all solutions of the assignment
        :return: unit success rate as a float [0;1]
        """
        return self.__calculate_weighted_average_divided__(test_results)

    def calculate_assignment_contains_testcase_success_rate(self,
                                                            test_results: list[WeightedExpectationTestResult]) -> float:
        """
        calculates the average contains success rate for a single assignment and contains testcase
        :param test_results: list of the most current weighted contains testresults for all solutions of the assignment and testcase
        :return: contains success rate as a float [0;1]
        """
        return self.__calculate_weighted_average_substract__(test_results)

    def __calculate_unweighted_average_list_multiple_assignments__(self, testresults_2dim: list[
        list[UnweightedTestResult]]) -> [float]:
        """
        calculates a list of unweighted averages for multiple assignment
        :param testresults_2dim: list of testresults for a tag. the 1st represents the assignments, the 2nd dimension represents the must current testresults for the assignment
        :return: list of unweighted averages for every testresult
        """
        average_success_list = []
        for test_results_for_single_solution in testresults_2dim:
            average_success_list.append(
                self.__calculate_unweighted_average_single_assignment__(test_results_for_single_solution))

        return average_success_list

    def __calculate_unweighted_average_single_assignment__(self, testresults: list[UnweightedTestResult]) -> float:
        """
        calculates the unweighted success rate of all testresults for a single assignment
        :param testresults: list of most current testresults for this assignment
        :return: unweighted average success rate as a float [0;1]
        """

        average_success = 0

        for testresult in testresults:
            average_success += (1 if testresult.success > 0 else 0)

        return average_success / len(testresults)

    def __calculate_weighted_average_divided__(self, testresults: list[WeightedExpectationTestResult]) -> float:
        """
        calculates the weighted success rate of all testresults for a single assignment. Weight is handled by division
        :param testresults: list of the most current weighted unit testresults for all solutions of the assignment
        :return: weighted success rate as a float [0;1]
        """
        average_success = 0

        for testresult in testresults:
            average_success += (testresult.reality / testresult.expectation)

        return average_success / len(testresults)

    def __calculate_weighted_average_substract__(self, testresults: list[WeightedExpectationTestResult]) -> float:
        """
        calculates the weighted success rate of all testresults for a single assignment. Weight is handled by subtraction
        :param testresults: list of the most current weighted unit testresults for all solutions of the assignment
        :return: weighted success rate as a float [0;1]
        """
        average_success = 0

        for testresult in testresults:
            average_success += abs(testresult.reality - testresult.expectation)

        return average_success / len(testresults)
