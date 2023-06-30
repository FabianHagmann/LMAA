import numpy as np
from javalang import tokenizer
from javalang.tokenizer import LexerError
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from scripts.visualization.metrics.halstead_cyclomatic.cyclomatic import calculate_cyclomatic
from scripts.visualization.metrics.halstead_cyclomatic.get_operators_operands_count import get_operators_operands_count
from scripts.visualization.metrics.halstead_cyclomatic.halstead import calculate_halstead


class SimilarityMetric:

    def calculate_cosine_similarity(self, solutions: dict[str, list[str]]):
        """
        calculates a cosine similarity between given solutions from (possible different) sources
        :param solutions: dictionary of source-[solutions]
        :return: the cosine similarity as a dictionary source-similarity
        """

        return_dict = {}
        vectorizer = TfidfVectorizer()

        for source in solutions.keys():
            tfidf_matrix = vectorizer.fit_transform(solutions.get(source))
            cosine_sim_matrix = cosine_similarity(tfidf_matrix)
            return_dict.__setitem__(source, cosine_sim_matrix)

        return return_dict

    def calculate_cosine_similarity_single_source(self, solutions: list[str]):
        """
        calculates a cosine similarity between given solution from a single source
        :param solutions: given solutions to calculate the cosine similarity for
        :return: the cosine similarity matrix for all given solutions
        """

        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(solutions)
        cosine_sim_matrix = cosine_similarity(tfidf_matrix)

        return cosine_sim_matrix

    def calculate_total_cosine_similarity_average(self, num_solutions, cosine_sim_matrix):
        """
        calculate the average of a cosine similarity matrix
        :param num_solutions: number of solutions
        :param cosine_sim_matrix: cosine similarity matrix
        :return: average cosine similarity of matrix
        """

        mask = np.ones(cosine_sim_matrix.shape, dtype=bool)
        np.fill_diagonal(mask, 0)

        average_similarity = np.sum(cosine_sim_matrix * mask) / (num_solutions * (num_solutions - 1))
        return average_similarity

    def calculate_total_cosine_similarity_median(self, num_solutions, cosine_sim_matrix):
        """
         calculate the median of a cosine similarity matrix
         :param num_solutions: number of solutions
         :param cosine_sim_matrix: cosine similarity matrix
         :return: median cosine similarity of matrix
         """

        mask = np.ones(cosine_sim_matrix.shape, dtype=bool)
        np.fill_diagonal(mask, 0)

        average_similarity = np.median(cosine_sim_matrix * mask)
        return average_similarity

    def calculate_cosine_similarity_min(self, cosine_sim_matrix):
        """
        find the minimal cosine similarity of a given matrix
        :param cosine_sim_matrix: cosine similarity matrix
        :return: minimum value found in the matrix
        """
        return cosine_sim_matrix.min()

    def calculate_cosine_similarity_max(self, cosine_sim_matrix):
        """
        find the maximum cosine similarity of a given matrix besides the diagonal
        :param cosine_sim_matrix: cosine similarity matrix
        :return: maximum value found in the matrix besides the diagonal
        """
        mask = np.ones(cosine_sim_matrix.shape, dtype=bool)
        np.fill_diagonal(mask, 0)

        return (cosine_sim_matrix * mask).max()

    def calculate_mccabe_complexity(self, solution: str) -> int:
        """
        calculate the cyclomatic complexity for a solution

        if the solution cannot be tokenized (no valid java code) -1 is returned

        :param solution: generated solution the cyc. complexity will be calculated for
        :return: calculated cyc. complexity or -1 is solution is not tokenizable
        """

        try:
            tokens = list(tokenizer.tokenize(solution))
        except LexerError:
            return -1

        operators, operands = get_operators_operands_count(tokens)

        return calculate_cyclomatic(operators)

    def calculate_halstead_metrics(self, solution: str) -> dict[str, float]:
        """
        calculate the halstead program length and volume for a given solution

        if the solution cannot be tokenized (no valid java code) -1 is returned for both

        :param solution: solution the program length and volume will be calculated for
        :return: program length and volume in a dictionary identified by "Program Length" and "Program Volume" (-1 is solution is not tokenizable)
        """
        try:
            tokens = list(tokenizer.tokenize(solution))
        except LexerError:
            return {
                'Program Length': -1,
                'Program Volume': -1
            }
        operators, operands = get_operators_operands_count(tokens)

        n1 = len(operators)
        n2 = len(operands)
        N1 = sum(operators.values())
        N2 = sum(operands.values())

        halstead_response = calculate_halstead(n1, N1, n2, N2)
        return {
            'Program Length': halstead_response['Program length'],
            'Program Volume': halstead_response['Volume']
        }
