import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.services.groq_service import chat_with_groq
from app.utils.store import record_event

logger = logging.getLogger("prepzo.chat")

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[Message]
    subject: Optional[str] = None
    examDate: Optional[str] = None
    mode: Optional[str] = None
    topics: Optional[List[str]] = None
    questionsContext: Optional[List[Dict[str, Any]]] = None
    # Enhanced context fields for deeper AI awareness
    studySchedule: Optional[List[Dict[str, Any]]] = None
    topicInsights: Optional[Dict[str, Any]] = None


@router.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Context-aware chatbot endpoint.

    Accepts optional mode, topics, questionsContext, studySchedule, and
    topicInsights so the AI can explain specific generated questions, reference
    the study schedule, and cite ML predictions in its coaching.
    """
    try:
        msgs = [{"role": m.role, "content": m.content} for m in request.messages]

        reply = chat_with_groq(
            messages=msgs,
            subject=request.subject,
            mode=request.mode,
            topics=request.topics,
            questions_context=request.questionsContext,
            exam_date=request.examDate,
            study_schedule=request.studySchedule,
            topic_insights=request.topicInsights,
        )

        record_event("chat_msg_sent")

        return {"reply": reply}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[Chat] Unexpected error: %s", e)
        raise HTTPException(
            status_code=500,
            detail="Chat service unavailable. Please try again in a moment.",
        )
