import logging
from fastapi import APIRouter, HTTPException
from app.models.schemas import GeneratePlanRequest, GeneratePlanResponse, Question, TopicInsight
from app.services.deadline_service import calculate_deadline_mode, assign_topic_weights, build_strategy
from app.services.groq_service import (
    generate_questions,
    parse_questions_from_response,
    _build_fallback_questions,
)
from app.services.ml_service import compute_topic_weights_tfidf, merge_weights, predict_question_types_batch
from app.services.spaced_repetition_service import generate_study_schedule
from app.utils.store import record_plan

logger = logging.getLogger("prepzo.plan")

router = APIRouter()


def _compute_focus_topics(questions: list, weights: dict, mode: str) -> list:
    """
    Derive focus topics from actual generated questions + topic weights.

    Scores each topic as: (avg probability of its questions × 0.6) + (weight × 0.4).
    This is smarter than a raw weight threshold because it reflects what the AI
    actually emphasised — topics that generated high-probability questions score
    higher than topics that appeared only in low-confidence questions.

    Falls back to including high-weight topics that the AI may have under-represented.
    """
    mode_limits = {"survival": 3, "balanced": 5, "full": 8}
    limit = mode_limits.get(mode, 5)

    topic_probs: dict = {}
    for q in questions:
        t = q.topic
        p = float(q.probability)
        if t not in topic_probs:
            topic_probs[t] = []
        topic_probs[t].append(p)

    topic_scores: dict = {}
    for t, probs in topic_probs.items():
        avg_prob = sum(probs) / len(probs)
        w = weights.get(t, 0.5)
        topic_scores[t] = round((avg_prob * 0.6) + (w * 0.4), 3)

    for t, w in weights.items():
        if t not in topic_scores and w >= 0.7:
            topic_scores[t] = round(w * 0.4, 3)

    sorted_topics = sorted(topic_scores.items(), key=lambda x: -x[1])
    return [t for t, _ in sorted_topics[:limit]]


@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    try:
        # Step 1: Determine mode from exam deadline
        mode = calculate_deadline_mode(request.examDate)

        # Step 2: Compute rule-based Pareto weights per mode
        rule_weights = assign_topic_weights(request.topics, mode)

        # Step 3: Blend in ML-derived TF-IDF weights if PDF was provided
        if request.pdfText:
            ml_weights = compute_topic_weights_tfidf(request.topics, request.pdfText)
            weights = merge_weights(rule_weights, ml_weights, ml_ratio=0.5)
        else:
            weights = rule_weights

        # Step 4: ML Model 2 — Predict question types per topic using Naive Bayes
        raw_insights = predict_question_types_batch(request.topics)
        topic_insights = {
            topic: TopicInsight(**data) for topic, data in raw_insights.items()
        }

        # Step 5: Generate questions — pass weights + ML insights so Groq obeys predictions
        raw_questions = generate_questions(
            subject=request.subject,
            topics=request.topics,
            mode=mode,
            weights=weights,
            pdf_text=request.pdfText,
            topic_insights=topic_insights,
        )

        # Step 6: Apply mode-aware priority scoring using blended weights
        parsed_questions = parse_questions_from_response(raw_questions, weights, mode)

        # Step 7: Convert to Pydantic models, skip any that fail validation
        questions = []
        for q in parsed_questions:
            try:
                questions.append(Question(**q))
            except Exception as e:
                logger.warning("[Plan] Skipping invalid question: %s | data: %s", e, q)

        # Last-resort safety net: if every question failed Pydantic validation
        if not questions:
            logger.error(
                "[Plan] All %d questions failed Pydantic validation — injecting fallbacks",
                len(parsed_questions),
            )
            fallback_raw = _build_fallback_questions(request.subject, request.topics, mode)
            fallback_parsed = parse_questions_from_response(fallback_raw, weights, mode)
            for q in fallback_parsed:
                try:
                    questions.append(Question(**q))
                except Exception as e:
                    logger.error("[Plan] Fallback question also failed validation: %s", e)

        logger.info(
            "[Plan] subject=%r mode=%s questions=%d",
            request.subject, mode, len(questions),
        )

        # Step 8: Derive focusTopics from actual AI output + weights
        focus_topics = _compute_focus_topics(questions, weights, mode)

        # Step 9: ML Model 4 — Generate SM-2 Spaced Repetition Study Schedule
        study_schedule = generate_study_schedule(
            topics=request.topics,
            exam_date=request.examDate,
            mode=mode,
            weights=weights,
        )

        # Step 10: Record analytics
        record_plan(request.subject, mode)

        return GeneratePlanResponse(
            mode=mode,
            focusTopics=focus_topics,
            strategy=build_strategy(mode),
            questions=questions,
            topicInsights=topic_insights,
            studySchedule=study_schedule,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[Plan] Unexpected error generating plan: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Failed to generate the study plan. Please try again.",
        )
