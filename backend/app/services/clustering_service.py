"""
ML Model 3 — Topic Clustering via K-Means

Automatically discovers topic groups from uploaded PDF text using
TF-IDF vectorization + K-Means clustering with elbow-method k selection.

When a student uploads a syllabus or past paper, this model segments the
text, vectorizes it, and clusters related content — surfacing structured
topic suggestions the student never had to type manually.
"""

import re
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger("prepzo.clustering")


# ─────────────────────────────────────────────
# Text Segmentation
# ─────────────────────────────────────────────

def _split_into_segments(text: str) -> list:
    """
    Split PDF text into meaningful segments for clustering.
    Handles numbered sections, bullet points, and paragraph breaks.
    """
    segments = re.split(r'\n\n+|\n\d+[\.\)]\s|\n[-•]\s', text)
    segments = [s.strip() for s in segments if len(s.strip()) > 20]
    return segments


# ─────────────────────────────────────────────
# Cluster Label Extraction
# ─────────────────────────────────────────────

def _extract_cluster_label(vectorizer, tfidf_matrix, cluster_indices: list) -> str:
    """Extract the most representative keyword(s) for a cluster."""
    if not cluster_indices:
        return "General"

    feature_names = vectorizer.get_feature_names_out()
    cluster_vectors = tfidf_matrix[cluster_indices]
    mean_vector = cluster_vectors.mean(axis=0).A1

    top_indices = mean_vector.argsort()[-3:][::-1]
    keywords = [feature_names[i] for i in top_indices if mean_vector[i] > 0]

    if keywords:
        return " & ".join(kw.title() for kw in keywords[:2])
    return "General"


# ─────────────────────────────────────────────
# Optimal K (Elbow Method)
# ─────────────────────────────────────────────

def _find_optimal_k(tfidf_matrix, max_k: int) -> int:
    """Find optimal number of clusters using simplified elbow method."""
    if max_k <= 2:
        return 2

    inertias = []
    k_range = range(2, max_k + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=5, max_iter=100)
        kmeans.fit(tfidf_matrix)
        inertias.append(kmeans.inertia_)

    if len(inertias) < 2:
        return 2

    # Find elbow: where the rate of inertia decrease sharply drops
    diffs = [inertias[i] - inertias[i + 1] for i in range(len(inertias) - 1)]
    for i in range(len(diffs) - 1):
        if diffs[i] > 0 and diffs[i + 1] / diffs[i] < 0.5:
            return list(k_range)[i + 1]

    return list(k_range)[len(k_range) // 2]


# ─────────────────────────────────────────────
# Public: Discover Topics from PDF
# ─────────────────────────────────────────────

def discover_topics_from_pdf(pdf_text: str, max_clusters: int = 8) -> dict:
    """
    Automatically discover topic clusters from PDF text using K-Means.

    Args:
        pdf_text: Raw text extracted from the PDF
        max_clusters: Maximum number of clusters to detect

    Returns:
        dict: {
            "clusters": [
                {
                    "label": "Data Structures & Algorithms",
                    "keywords": ["array", "linked list", "tree", "sort", "search"],
                    "segment_count": 5,
                    "confidence": 0.85
                }
            ],
            "suggested_topics": ["Data Structures & Algorithms", ...]
        }
    """
    if not pdf_text or len(pdf_text.strip()) < 50:
        return {"clusters": [], "suggested_topics": []}

    segments = _split_into_segments(pdf_text)

    if len(segments) < 3:
        return {"clusters": [], "suggested_topics": []}

    # Cap clusters based on available data
    max_k = min(max_clusters, len(segments) // 2, len(segments) - 1)
    max_k = max(2, max_k)

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            max_features=500,
            min_df=1,
            max_df=0.95,
            ngram_range=(1, 2),
        )
        tfidf_matrix = vectorizer.fit_transform(segments)

        if tfidf_matrix.shape[0] < 2:
            return {"clusters": [], "suggested_topics": []}

        best_k = _find_optimal_k(tfidf_matrix, max_k)

        kmeans = KMeans(n_clusters=best_k, random_state=42, n_init=10, max_iter=300)
        labels = kmeans.fit_predict(tfidf_matrix)

        feature_names = vectorizer.get_feature_names_out()
        clusters = []

        for cluster_id in range(best_k):
            indices = [i for i, lbl in enumerate(labels) if lbl == cluster_id]
            if not indices:
                continue

            # Top keywords from cluster center
            center = kmeans.cluster_centers_[cluster_id]
            top_kw_indices = center.argsort()[-5:][::-1]
            keywords = [feature_names[i] for i in top_kw_indices if center[i] > 0]

            label = _extract_cluster_label(vectorizer, tfidf_matrix, indices)

            # Confidence = average cosine similarity to cluster center
            cluster_vectors = tfidf_matrix[indices]
            sims = cosine_similarity(
                cluster_vectors,
                kmeans.cluster_centers_[cluster_id : cluster_id + 1],
            )
            confidence = float(np.mean(sims))

            clusters.append(
                {
                    "label": label,
                    "keywords": keywords[:5],
                    "segment_count": len(indices),
                    "confidence": round(max(0.0, min(1.0, confidence)), 3),
                }
            )

        clusters.sort(key=lambda c: -c["segment_count"])
        suggested_topics = [c["label"] for c in clusters if c["confidence"] > 0.1]

        logger.info(
            "[Clustering] Discovered %d clusters from %d segments (k=%d)",
            len(clusters),
            len(segments),
            best_k,
        )
        return {"clusters": clusters, "suggested_topics": suggested_topics}

    except Exception as e:
        logger.error("[Clustering] Error: %s", e)
        return {"clusters": [], "suggested_topics": []}
