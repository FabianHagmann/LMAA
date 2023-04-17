
class TestcaseForSuccessMetric:

    def __init__(self, weight: float, success: float) -> None:
        """
        Creates a testcase result for use in success metric calculations
        :param weight: weight of the particular testcase [1;inf]
        :param success: success-rate of the particular testcase [0;1]
        """
        self.weight = weight
        self.success = success


class SuccessMetric:

    def calculate_success_rate_single_solution(self, testcases: list[TestcaseForSuccessMetric]) -> float:
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

        return weight_success/weight_total

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

    def calculate_success_rate_multiple_solutions(self,  testcase_2dim) -> float:
        """
        calculates a single success rate of a 2 dimensional list of testcases
        :param testcase_2dim: list of list of testcases
        :return: success rate as a float [0;1]
        """
        success_rate_list = self.calculate_success_dict_multiple_solutions(testcase_2dim)

        success_rate_sum = 0
        for success_rate in success_rate_list:
            success_rate_sum += success_rate

        return success_rate_sum/len(success_rate_list)