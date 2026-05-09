import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.utils.pdf_parser import extract_text_from_pdf, extract_topics_from_text
from app.services.clustering_service import discover_topics_from_pdf
from app.services.pattern_analyzer_service import analyze_patterns

logger = logging.getLogger("prepzo.upload")

router = APIRouter()

MAX_PDF_BYTES = 10 * 1024 * 1024  # 10 MB


@router.post("/upload-pdf")
async def analyze_input(file: UploadFile = File(...)):
    """
    Upload a PDF (syllabus/notes/past papers) and run the full ML pipeline:
      1. Extract text (pdfplumber)
      2. Detect topics (heuristic bullet/number detection)
      3. ML Model 3 — K-Means topic clustering (auto-discover topic groups)
      4. ML Model 5 — Cosine similarity pattern analysis (detect repeating questions)
    """
    # Validate file type
    if file.content_type not in ("application/pdf", "application/octet-stream") and not (
        file.filename or ""
    ).lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    temp_file_path = f"temp_{file.filename}"

    try:
        # Read and check file size before writing
        content = await file.read()
        if len(content) > MAX_PDF_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum allowed size is 10 MB.",
            )

        with open(temp_file_path, "wb") as buffer:
            buffer.write(content)

        extracted_text = extract_text_from_pdf(temp_file_path)

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=422,
                detail="Could not extract text from this PDF. Make sure it is not scanned/image-only.",
            )

        detected_topics = extract_topics_from_text(extracted_text)

        # ML Model 3: K-Means Clustering — auto-discover topic groups
        clustering_result = discover_topics_from_pdf(extracted_text)

        # Merge heuristic topics with ML-discovered topics (deduplicated)
        suggested = clustering_result.get("suggested_topics", [])
        all_topics = list(dict.fromkeys(detected_topics + suggested))

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
            "extracted_text_preview": (
                extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
            ),
            "detectedTopics": all_topics,
            "clustering": clustering_result,
            "patternAnalysis": pattern_result,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[Upload] Unexpected error processing %s: %s", file.filename, e)
        raise HTTPException(
            status_code=500,
            detail="Failed to process the PDF. Please try again or use a different file.",
        )
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
