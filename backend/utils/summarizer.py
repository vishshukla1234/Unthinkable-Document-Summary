"""
Extractive text summarization using the TextRank algorithm, implemented
entirely with local libraries (scikit-learn + networkx). No calls to any
external AI / LLM API are made -- this is a classic graph-based ranking
algorithm (Mihalcea & Tarau, 2004).

Approach:
  1. Split the document into sentences (regex-based, no nltk download needed).
  2. Vectorize sentences with TF-IDF.
  3. Build a sentence-similarity graph (cosine similarity).
  4. Run PageRank over the graph to score each sentence's "importance".
  5. Select the top-N highest scoring sentences for the summary, and output
     them back in their original document order (so the summary still reads
     naturally). The very top sentences are also returned separately as
     "key points".
"""

import re
import numpy as np
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

LENGTH_CONFIG = {
    "short": {"ratio": 0.15, "min_sentences": 2, "max_sentences": 5},
    "medium": {"ratio": 0.30, "min_sentences": 4, "max_sentences": 10},
    "long": {"ratio": 0.50, "min_sentences": 6, "max_sentences": 20},
}

SENTENCE_SPLIT_RE = re.compile(
    r"(?<!\b[A-Z])(?<!\bMr)(?<!\bMrs)(?<!\bMs)(?<!\bDr)(?<!\bvs)(?<=[.!?])\s+(?=[A-Z\"'(])"
)


def split_into_sentences(text: str):
    cleaned = re.sub(r"\s*\n\s*", " ", text)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip()
    if not cleaned:
        return []

    raw_sentences = SENTENCE_SPLIT_RE.split(cleaned)
    sentences = [s.strip() for s in raw_sentences if len(s.strip()) > 0]
    sentences = [s for s in sentences if len(s.split()) >= 4]
    return sentences


def _target_sentence_count(n_sentences: int, length: str) -> int:
    config = LENGTH_CONFIG.get(length, LENGTH_CONFIG["medium"])
    target = max(config["min_sentences"], round(n_sentences * config["ratio"]))
    target = min(target, config["max_sentences"], n_sentences)
    return max(target, 1)


def summarize(text: str, length: str = "medium", key_point_count: int = 5) -> dict:
    sentences = split_into_sentences(text)

    if len(sentences) == 0:
        return {
            "summary": "",
            "key_points": [],
            "sentence_count": 0,
            "original_sentence_count": 0,
        }

    if len(sentences) <= 2:
        return {
            "summary": " ".join(sentences),
            "key_points": sentences,
            "sentence_count": len(sentences),
            "original_sentence_count": len(sentences),
        }

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform(sentences)
    except ValueError:
        return {
            "summary": " ".join(sentences[: min(3, len(sentences))]),
            "key_points": sentences[: min(3, len(sentences))],
            "sentence_count": min(3, len(sentences)),
            "original_sentence_count": len(sentences),
        }

    similarity_matrix = cosine_similarity(tfidf_matrix)
    np.fill_diagonal(similarity_matrix, 0)

    graph = nx.from_numpy_array(similarity_matrix)
    try:
        scores = nx.pagerank(graph, max_iter=200)
    except nx.PowerIterationFailedConvergence:
        scores = {i: float(np.sum(similarity_matrix[i])) for i in range(len(sentences))}

    ranked_indices = sorted(scores, key=lambda i: scores[i], reverse=True)

    target_count = _target_sentence_count(len(sentences), length)
    top_indices_for_summary = sorted(ranked_indices[:target_count])
    summary_sentences = [sentences[i] for i in top_indices_for_summary]

    key_point_indices = ranked_indices[: min(key_point_count, len(sentences))]
    key_points = [sentences[i] for i in key_point_indices]

    return {
        "summary": " ".join(summary_sentences),
        "key_points": key_points,
        "sentence_count": len(summary_sentences),
        "original_sentence_count": len(sentences),
    }
