from scripts.visualization.metrics.similarity_metric import SimilarityMetric
from scripts.visualization.metrics.success_metric import SuccessMetric, TestresultForSuccessMetric


class MetricsManager:

    def __init__(self) -> None:
        self.__similarity_metric__ = SimilarityMetric()
        self.__success_metric__ = SuccessMetric()

    def similarity_cosine_single_source(self, solutions: list[str]):
        return self.__similarity_metric__.calculate_cosine_similarity_single_source(solutions)

    def similarity_cosine_multiple_source(self, solutions: dict[str, list[str]]):
        return self.__similarity_metric__.calculate_cosine_similarity(solutions)

    def similarity_cosine_average(self, num_solutions, cosine_sim_matrix):
        return self.__similarity_metric__.calculate_total_similarity_average(num_solutions, cosine_sim_matrix)

    def similarity_cosine_median(self, num_solutions, cosine_sim_matrix):
        return self.__similarity_metric__.calculate_total_similarity_median(num_solutions, cosine_sim_matrix)

    def success_rate_multiple_solutions(self, testresults: list[list[TestresultForSuccessMetric]]):
        return self.__success_metric__.calculate_success_rate_multiple_solutions(testresults)
