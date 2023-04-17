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

    def calculate_total_similarity_average(self, num_solutions, cosine_sim_matrix):
        mask = np.ones(cosine_sim_matrix.shape, dtype=bool)
        np.fill_diagonal(mask, 0)

        average_similarity = np.sum(cosine_sim_matrix * mask) / (num_solutions * (num_solutions - 1))
        return average_similarity

    def calculate_total_similarity_median(self, num_solutions, cosine_sim_matrix):
        mask = np.ones(cosine_sim_matrix.shape, dtype=bool)
        np.fill_diagonal(mask, 0)

        average_similarity = np.median(cosine_sim_matrix * mask) / (num_solutions * (num_solutions - 1))
        return average_similarity

