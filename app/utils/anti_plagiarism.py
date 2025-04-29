from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def check_plagiarism(answers, threshold=0.9):
    """
    Compare answers for similarity and flag potential plagiarism.
    :param answers: List of answer texts
    :param threshold: Similarity threshold for flagging
    :return: List of tuples (answer_id, similar_answer_id, similarity_score)
    """
    if len(answers) < 2:
        return []

    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(answers)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    plagiarism_cases = []
    for i in range(len(answers)):
        for j in range(i + 1, len(answers)):
            if similarity_matrix[i][j] > threshold:
                plagiarism_cases.append((i, j, similarity_matrix[i][j]))
    return plagiarism_cases