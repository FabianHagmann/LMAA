import math
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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
        calculate the cyclomatic complexity of a single given solution
        :param solution:
        :return:
        """
        keywords = ["if", "else", "while", "case", "for", "switch", "do", "continue", "break", "&&", "||", "?", ":",
                    "catch", "finally", "throw", "throws", "default", "return"]

        def extract_decision_points(solution_lines):
            """
            find the decision points in the solution
            :param solution_lines: seperated lines of the solution as array
            :return: number of found decision points in solution
            """
            decision_points = 0

            for line in solution_lines:
                line = line.strip()
                # Skip comments and string literals
                if line.startswith('//') or line.startswith('/*') or line.startswith('*') or line.endswith(
                        '*/') or line.startswith('import'):
                    continue

                for word in keywords:
                    decision_points += line.count(word)

            return decision_points

        def mccabe_complexity(file_path):
            """
            calculate final cyclomatic complexity
            :param file_path:
            :return:
            """
            decision_points = extract_decision_points(file_path)
            return decision_points + 1

        sol_lines = solution.split('\n')
        complexity = mccabe_complexity(sol_lines)
        return complexity

    def calculate_halstead_metrics(self, solution: str) -> dict[str, float]:
        """
        calculate the halstead program length and volume for a single solution
        :param solution: solution to calculate for
        :return: dict containging the program length and volume
        """

        operators = {
            '+', '-', '*', '/', '%', '++', '--',
            '==', '!=', '>', '<', '>=', '<=',
            '&&', '||', '!', '&', '|', '^', '~', '<<', '>>', '>>>',
            '=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '<<=', '>>=', '>>>=',
            '(', ')', '{', '}', '[', ']',
            ';', ',', '.', '::'
        }

        def extract_operators_operands(solution_lines):
            """
            find the number of operators and operands in the solution
            :param solution_lines: seperated lines of the solution as array
            :return: count of operators and operands
            """
            operators_count = {}
            operands_count = {}

            for line in solution_lines:
                line = re.sub(r'\".*?\"|\'.*?\'', '', line)  # remove string literals
                line = re.sub(r'\/\/.*', '', line)  # remove single-line comments
                for op in operators:
                    count = line.count(op)
                    if count > 0:
                        operators_count[op] = operators_count.get(op, 0) + count
                words = re.findall(r'\b\w+\b', line)
                for word in words:
                    if word not in operators:
                        operands_count[word] = operands_count.get(word, 0) + 1

            return operators_count, operands_count

        def halstead_metrics(operators_count, operands_count):
            """
            calculate the program length and volume
            :param operators_count: number of operators in solution
            :param operands_count: number of operands in solution
            :return: dict containing program length and volume
            """
            n1 = sum(operators_count.values())
            n2 = sum(operands_count.values())
            N1 = len(operators_count)
            N2 = len(operands_count)

            n = n1 + n2
            N = N1 + N2
            V = N * math.log2(n)

            return {
                'Program Length': N,
                'Program Volume': V
            }

        sol_lines = solution.split('\n')
        operators_count, operands_count = extract_operators_operands(sol_lines)
        metrics = halstead_metrics(operators_count, operands_count)
        return metrics
