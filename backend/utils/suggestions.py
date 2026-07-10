"""
"Improvement Suggestions" feature.

Everything here is computed with plain heuristics/statistics -- no external
API calls. It looks at readability, sentence length, passive voice,
word repetition, and overall structure, and returns actionable tips.
"""

import re
from collections import Counter

PASSIVE_RE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+\w+ed\b|\b(am|is|are|was|were|be|been|being)\s+\w+en\b",
    re.IGNORECASE,
)

STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "with", "as", "by", "at", "is", "are", "was", "were", "be", "been",
    "this", "that", "these", "those", "it", "its", "from", "which", "who",
    "will", "would", "can", "could", "should", "may", "might", "not",
    "have", "has", "had", "do", "does", "did", "so", "than", "then",
}


def _count_syllables(word: str) -> int:
    word = word.lower()
    word = re.sub(r"[^a-z]", "", word)
    if not word:
        return 0
    groups = re.findall(r"[aeiouy]+", word)
    count = len(groups)
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def _flesch_reading_ease(sentences, words):
    if not sentences or not words:
        return None
    total_syllables = sum(_count_syllables(w) for w in words)
    words_per_sentence = len(words) / len(sentences)
    syllables_per_word = total_syllables / len(words)
    score = 206.835 - (1.015 * words_per_sentence) - (84.6 * syllables_per_word)
    return round(score, 1)


def _readability_label(score):
    if score is None:
        return "Unknown"
    if score >= 90:
        return "Very Easy"
    if score >= 70:
        return "Easy"
    if score >= 60:
        return "Fairly Easy"
    if score >= 50:
        return "Standard"
    if score >= 30:
        return "Fairly Difficult"
    return "Difficult"


def generate_suggestions(text: str, sentences: list) -> dict:
    words = re.findall(r"[A-Za-z']+", text)
    suggestions = []

    # --- Readability ---
    flesch_score = _flesch_reading_ease(sentences, words)
    readability_label = _readability_label(flesch_score)
    if flesch_score is not None and flesch_score < 50:
        suggestions.append({
            "category": "Readability",
            "message": (
                f"Readability score is {flesch_score} ({readability_label}). "
                "Consider using simpler vocabulary and shorter sentences to make "
                "the document easier to read."
            ),
        })

    # --- Sentence length ---
    if sentences:
        sentence_lengths = [len(s.split()) for s in sentences]
        avg_len = sum(sentence_lengths) / len(sentence_lengths)
        long_sentence_count = sum(1 for l in sentence_lengths if l > 30)
        if avg_len > 25:
            suggestions.append({
                "category": "Sentence Length",
                "message": (
                    f"Average sentence length is {avg_len:.1f} words. Long, "
                    "complex sentences reduce clarity -- try breaking them into "
                    "shorter, more direct sentences."
                ),
            })
        if long_sentence_count > 0:
            suggestions.append({
                "category": "Sentence Length",
                "message": (
                    f"{long_sentence_count} sentence(s) exceed 30 words. "
                    "Consider splitting these into two or more sentences."
                ),
            })

    # --- Passive voice ---
    passive_hits = len(PASSIVE_RE.findall(text))
    if sentences and passive_hits > max(2, len(sentences) * 0.2):
        suggestions.append({
            "category": "Writing Style",
            "message": (
                f"Detected roughly {passive_hits} instances of passive voice. "
                "Using more active voice generally makes writing more direct "
                "and engaging."
            ),
        })

    # --- Repetition ---
    lowered_words = [w.lower() for w in words if w.lower() not in STOPWORDS and len(w) > 3]
    counts = Counter(lowered_words)
    repeated = [w for w, c in counts.most_common(5) if c >= max(5, len(words) // 40)]
    if repeated:
        suggestions.append({
            "category": "Word Variety",
            "message": (
                "These words are repeated frequently: "
                f"{', '.join(repeated)}. Consider using synonyms to vary the "
                "language and reduce repetition."
            ),
        })

    # --- Structure / length of document ---
    if len(sentences) < 5:
        suggestions.append({
            "category": "Content Depth",
            "message": (
                "The document is quite short. If this is meant to be a "
                "comprehensive document, consider adding more supporting "
                "detail, examples, or context."
            ),
        })
    elif len(sentences) > 120:
        suggestions.append({
            "category": "Structure",
            "message": (
                "This is a long document. Consider adding headings, "
                "sections, or bullet points to improve scannability."
            ),
        })

    if not suggestions:
        suggestions.append({
            "category": "General",
            "message": "The document reads well overall -- no major issues detected.",
        })

    return {
        "suggestions": suggestions,
        "readability": {
            "flesch_score": flesch_score,
            "label": readability_label,
        },
    }
