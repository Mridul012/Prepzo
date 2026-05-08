import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File
from app.utils.pdf_parser import extract_text_from_pdf, extract_topics_from_text
from app.services.clustering_service import discover_topics_from_pdf
from app.services.pattern_analyzer_service import analyze_patterns

logger = logging.getLogger("prepzo.upload")

router = APIRouter()

@router.post("/upload-pdf")
async def analyze_input(file: UploadFile = File(...)):
    """
    Upload a PDF (syllabus/notes/past papers) and run the full ML pipeline:
      1. Extract text (pdfplumber)
      2. Detect topics (heuristic bullet/number detection)
      3. ML Model 3 — K-Means topic clustering (auto-discover topic groups)
      4. ML Model 5 — Cosine similarity pattern analysis (detect repeating questions)
    """
    temp_file_path = f"temp_{file.filename}"

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    extracted_text = extract_text_from_pdf(temp_file_path)
    detected_topics = extract_topics_from_text(extracted_text)

    # Clean up temp file
    if os.path.exists(temp_file_path):
        os.remove(temp_file_path)

    # ML Model 3: K-Means Clustering — auto-discover topic groups
    clustering_result = discover_topics_from_pdf(extracted_text)

    # Merge heuristic topics with ML-discovered topics (deduplicated)
    suggested = clustering_result.get("suggested_topics", [])
    all_topics = list(dict.fromkeys(detected_topics + suggested))  # preserve order, dedup

    # ML Model 5: Pattern Analysis — detect repeating question patterns
    pattern_result = analyze_patterns(extracted_text, all_topics)

    logger.info(
        "[Upload] file=%s | heuristic_topics=%d | clusters=%d | patterns=%d | questions_analyzed=%d",
        file.filename,
        len(detected_topics),
        len(clustering_result.get("clusters", [])),
        len(pattern_result.get("patterns", [])),
        pattern_result.get("totalQuestionsAnalyzed", 0),
    )

    return {
        "filename": file.filename,
        "extracted_text_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
        "detectedTopics": all_topics,
        "clustering": clustering_result,
        "patternAnalysis": pattern_result,
    }
