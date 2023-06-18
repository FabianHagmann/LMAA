from scripts.visualization.metrics.similarity_metric import SimilarityMetric
from scripts.visualization.metrics.success_metric import SuccessMetric, UnweightedTestResult


class MetricsManager:

    def __init__(self) -> None:
        self.__similarity_metric__ = SimilarityMetric()
        self.__success_metric__ = SuccessMetric()

    def similarity_cosine_single_source(self, solutions: list[str]):
        """
        calculate the cosine similarity for a list of solutions
        :param solutions: list of solutions
        :return: calculated cosine similarity matrix
        """

        return self.__similarity_metric__.calculate_cosine_similarity_single_source(solutions)

    def similarity_cosine_multiple_source(self, solutions: dict[str, list[str]]):
        """
        calculate the cosine similarity for separately for multiple communicators
        :param solutions: dict of solutions per communicator
        :return: the cosine similarity as a dict source-similarity_matrix
        """
        return self.__similarity_metric__.calculate_cosine_similarity(solutions)

    def similarity_cosine_average(self, num_solutions, cosine_sim_matrix):
        """
        calculate the average of a cosine similarity matrix
        :param num_solutions: number of solutions
        :param cosine_sim_matrix: cosine similarity matrix
        :return: average cosine similarity of matrix
        """
        return self.__similarity_metric__.calculate_total_cosine_similarity_average(num_solutions, cosine_sim_matrix)

    def similarity_cosine_median(self, num_solutions, cosine_sim_matrix):
        """
        calculate the median of a cosine similarity matrix
        :param num_solutions: number of solutions
        :param cosine_sim_matrix: cosine similarity matrix
        :return: median cosine similarity of matrix
        """
        return self.__similarity_metric__.calculate_total_cosine_similarity_median(num_solutions, cosine_sim_matrix)

    def similarity_cosine_min(self, cosine_sim_matrix):
        """
        find the minimal cosine similarity of a given matrix
        :param cosine_sim_matrix: cosine similarity matrix
        :return: minimum value found in the matrix
        """
        return self.__similarity_metric__.calculate_cosine_similarity_min(cosine_sim_matrix)

    def similarity_cosine_max(self, cosine_sim_matrix):
        """
        find the maximum cosine similarity of a given matrix besides the diagonal
        :param cosine_sim_matrix: cosine similarity matrix
        :return: maximum value found in the matrix besides the diagonal
        """
        return self.__similarity_metric__.calculate_cosine_similarity_max(cosine_sim_matrix)

    def halstead_metrics(self, solutions: dict[int, str]) -> dict[int, dict[str, float]]:
        """
        calculate the halstead metrics for a list of solutions
        :param solutions: dict containing solutions mapped by their id
        :return: halstead metrics as a dict mapped by the solution id
        """
        return_dict = {}
        for id in solutions.keys():
            sol = solutions.get(id)
            return_dict.__setitem__(id, self.__similarity_metric__.calculate_halstead_metrics(sol))
        return return_dict

    def mccabe_complexity(self, solutions: dict[int, str]) -> dict[int, int]:
        """
        calculate the cyclomatic complexity of a dict of solutions
        :param solutions: dict of solutions mapped by the solution id
        :return: dict of cyclomatic complexities mapped by the solution id
        """
        return_dict = {}
        for id in solutions.keys():
            sol = solutions.get(id)
            return_dict.__setitem__(id, self.__similarity_metric__.calculate_mccabe_complexity(sol))
        return return_dict

    def success_rate_compiles(self, testresults: list[list[UnweightedTestResult]]) -> float:
        """
        calculate the average compiles success rate for a 2dim list of unweighted testresults
        :param testresults: 2dim compiles testresults (as unweighted testresults)
        :return: average compiles success rate
        """
        return self.__success_metric__.calculate_tag_compiles_success_rate(testresults)

