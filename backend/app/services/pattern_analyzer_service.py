"""
ML Model 5 — Question Pattern Analyzer (Cosine Similarity Matrix)

Analyzes uploaded past papers to detect repeating question patterns
using TF-IDF vectorization and pairwise cosine similarity.

When questions cluster together with high similarity scores, it means
the examiner repeatedly tests that concept — giving us a data-driven
probability estimate for each question type.
"""

import re
import logging
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("prepzo.pattern_analyzer")


# ─────────────────────────────────────────────
# Question Extraction from Raw Text
# ─────────────────────────────────────────────

def _extract_questions_from_text(text: str) -> list:
    """Extract individual questions from past paper text."""
    patterns = [
        r'(?:Q\.?\s*\d+|Question\s+\d+)[.:)]\s*(.+?)(?=(?:Q\.?\s*\d+|Question\s+\d+)[.:)]|\Z)',
        r'(?:\d+[\.\)]\s*)(.+?)(?=\d+[\.\)]\s|\Z)',
        r'(?:^|\n)\s*(?:[a-z]\)|[ivx]+\))\s*(.+?)(?=(?:^|\n)\s*(?:[a-z]\)|[ivx]+\))|\Z)',
    ]

    questions = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE | re.IGNORECASE)
        for m in matches:
            cleaned = m.strip().replace("\n", " ")
            if 15 < len(cleaned) < 500:
                questions.append(cleaned)

    # Fallback: sentences containing question marks
    if not questions:
        sentences = re.split(r'[.?]\s+', text)
        questions = [s.strip() for s in sentences if len(s.strip()) > 20 and '?' in s]

    # Last resort: meaningful lines
    if not questions:
        lines = text.split('\n')
        questions = [l.strip() for l in lines if len(l.strip()) > 20]

    return questions[:50]


# ─────────────────────────────────────────────
# Question Category Classification
# ─────────────────────────────────────────────

_CATEGORY_RULES = [
    (["write a program", "implement", "code", "algorithm", "function", "class"], "Implementation/Coding"),
    (["define", "what is", "meaning", "state the"], "Definition/Recall"),
    (["compare", "difference", "distinguish", "versus", " vs "], "Comparison"),
    (["explain", "describe", "discuss", "elaborate"], "Explanation"),
    (["advantage", "disadvantage", "pros", "cons", "merit", "demerit"], "Analysis"),
    (["design", "architecture", "diagram", "draw"], "Design"),
    (["which of", "select", "choose", "true or false", "correct option"], "MCQ/Objective"),
    (["list", "enumerate", "name the", "mention"], "Listing"),
    (["solve", "calculate", "find the", "compute", "evaluate"], "Problem Solving"),
]


def _classify_question_pattern(question: str) -> str:
    """Classify a question into a broad pattern category."""
    q_lower = question.lower()
    for keywords, category in _CATEGORY_RULES:
        if any(kw in q_lower for kw in keywords):
            return category
    return "General Theory"


# ─────────────────────────────────────────────
# Public: Analyze Question Patterns
# ─────────────────────────────────────────────

def analyze_patterns(pdf_text: str, topics: list = None) -> dict:
    """
    Analyze past paper text to detect repeating question patterns
    using a cosine similarity matrix.

    Args:
        pdf_text: Raw text from uploaded past papers
        topics: Optional list of topics to correlate with

    Returns:
        dict: {
            "patterns": [
                {
                    "pattern": "Explain the working of...",
                    "category": "Explanation",
                    "frequency": 4,
                    "probability": 0.92,
                    "similar_questions": ["Explain...", "Describe..."]
                }
            ],
            "categoryBreakdown": {
                "Explanation": 35,
                "Comparison": 20
            },
            "topicCorrelation": {
                "Arrays": {"most_common_type": "Implementation/Coding", "frequency": 5}
            },
            "totalQuestionsAnalyzed": 25
        }
    """
    empty = {
        "patterns": [],
        "categoryBreakdown": {},
        "topicCorrelation": {},
        "totalQuestionsAnalyzed": 0,
    }

    if not pdf_text or len(pdf_text.strip()) < 50:
        return empty

    questions = _extract_questions_from_text(pdf_text)
    if len(questions) < 2:
        return {**empty, "totalQuestionsAnalyzed": len(questions)}

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=300,
            min_df=1,
            ngram_range=(1, 2),
        )
        tfidf_matrix = vectorizer.fit_transform(questions)

        # Pairwise cosine similarity
        sim_matrix = cosine_similarity(tfidf_matrix)

        # Group similar questions (threshold > 0.3)
        THRESHOLD = 0.3
        visited = set()
        pattern_groups = []

        for i in range(len(questions)):
            if i in visited:
                continue
            group = [i]
            visited.add(i)
            for j in range(i + 1, len(questions)):
                if j not in visited and sim_matrix[i][j] > THRESHOLD:
                    group.append(j)
                    visited.add(j)
            pattern_groups.append(group)

        # Build pattern results
        patterns = []
        category_counts = {}

        for group in pattern_groups:
            representative = questions[group[0]]
            category = _classify_question_pattern(representative)
            frequency = len(group)
            probability = min(0.99, round(0.50 + (frequency / len(questions)) * 0.49, 2))
            similar = [questions[i][:120] for i in group[:5]]

            patterns.append(
                {
                    "pattern": representative[:150],
                    "category": category,
                    "frequency": frequency,
                    "probability": probability,
                    "similar_questions": similar,
                }
            )
            category_counts[category] = category_counts.get(category, 0) + frequency

        patterns.sort(key=lambda p: -p["frequency"])

        # Category breakdown (percentages)
        total = sum(category_counts.values()) or 1
        category_breakdown = {
            k: round((v / total) * 100)
            for k, v in sorted(category_counts.items(), key=lambda x: -x[1])
        }

        # Topic correlation
        topic_correlation = {}
        if topics:
            for topic in topics:
                topic_lower = topic.lower()
                matching_cats = []
                freq = 0
                for q in questions:
                    if topic_lower in q.lower():
                        matching_cats.append(_classify_question_pattern(q))
                        freq += 1
                if matching_cats:
                    most_common = Counter(matching_cats).most_common(1)[0][0]
                    topic_correlation[topic] = {
                        "most_common_type": most_common,
                        "frequency": freq,
                    }

        logger.info(
            "[PatternAnalyzer] Analyzed %d questions → %d patterns, %d categories",
            len(questions),
            len(patterns),
            len(category_breakdown),
        )
        return {
            "patterns": patterns[:15],
            "categoryBreakdown": category_breakdown,
            "topicCorrelation": topic_correlation,
            "totalQuestionsAnalyzed": len(questions),
        }

    except Exception as e:
        logger.error("[PatternAnalyzer] Error: %s", e)
        return empty
