from gui.testing.models import UnitTestresult, ContainsTestresult, CompilesTestresult

class TestresultForSuccessMetric:

    def __init__(self, weight: float, success: float) -> None:
        """
        Creates a testcase result for use in success metric calculations
        :param weight: weight of the particular testcase [1;inf]
        :param success: success-rate of the particular testcase [0;1]
        """
        self.weight = weight
        self.success = success

    @staticmethod
    def fromUnitTestresult(testresults: list[UnitTestresult]):
        result_list = []
        for single_testresult in testresults:
            success_rate = single_testresult.success_testcases / single_testresult.total_testcases
            result_list.append(TestresultForSuccessMetric(weight=single_testresult.total_testcases, success=success_rate))
        return result_list

    @staticmethod
    def fromContainsTestresult(testresults: list[ContainsTestresult]):
        result_list = []
        for single_testresult in testresults:
            if single_testresult.count_found < single_testresult.count_wanted:
                if single_testresult.count_wanted != 0:
                    # e.g. 1/2, 0/1
                    success_rate = single_testresult.count_found / single_testresult.count_wanted
                else:
                    # invalid option: found < 0, wanted = 0
                    success_rate = 0
            elif single_testresult.count_found > single_testresult.count_wanted:
                if single_testresult.count_wanted != 0:
                    # e.g. 2/1, 3/2
                    success_rate = single_testresult.count_wanted / single_testresult.count_found
                else:
                    # e.g. 1/0, 2/0
                    success_rate = 0
            else:
                success_rate = 1

            result_list.append(TestresultForSuccessMetric(weight=single_testresult.count_wanted, success=success_rate))
        return result_list

    @staticmethod
    def fromCompilesTestresult(testresults: list[CompilesTestresult]):
        result_list = []
        for single_testresult in testresults:
            success_rate = 1 if single_testresult.result else 0
            result_list.append(TestresultForSuccessMetric(weight=1, success=success_rate))
        return result_list


class SuccessMetric:

    def calculate_success_rate_single_solution(self, testcases: list[TestresultForSuccessMetric]) -> float:
        """
        calculates the success rate of all given testcases
        :param testcases: given testcases to calculate the success rate for
        :return: success rate as a float [0;1]
        """

        weight_total = 0
        weight_success = 0

        for testcase in testcases:
            weight_total += testcase.weight
            weight_success += (testcase.weight * testcase.success)

        return weight_success / weight_total

    def calculate_success_dict_multiple_solutions(self, testcase_2dim) -> [float]:
        """
        calculates the success rates of a 2 dimensional list of testcases
        :param testcase_2dim: list of list of testcases
        :return: list of success_rates for every set of testcases
        """
        success_rate_list = []
        for testcases in testcase_2dim:
            success_rate_list.append(self.calculate_success_rate_single_solution(testcases))

        return success_rate_list

    def calculate_success_rate_multiple_solutions(self, testcase_2dim) -> float:
        """
        calculates a single success rate of a 2 dimensional list of testcases
        :param testcase_2dim: list of list of testcases
        :return: success rate as a float [0;1]
        """
        success_rate_list = self.calculate_success_dict_multiple_solutions(testcase_2dim)

        success_rate_sum = 0
        for success_rate in success_rate_list:
            success_rate_sum += success_rate

        return success_rate_sum / len(success_rate_list)
