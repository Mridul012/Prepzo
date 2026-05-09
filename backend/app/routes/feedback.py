from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.utils.feedback_store import add_feedback, get_all_feedback, get_average_rating

router = APIRouter()

class FeedbackRequest(BaseModel):
    studentName: Optional[str] = "Anonymous"
    subject: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    review: str = Field(..., min_length=5)

@router.post("/feedback")
async def submit_feedback(req: FeedbackRequest):
    if req.rating < 1 or req.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")
    
    entry = {
        "studentName": req.studentName,
        "subject": req.subject,
        "rating": req.rating,
        "review": req.review,
        "submittedAt": datetime.now().isoformat(),
    }
    add_feedback(entry)
    return {"message": "Thank you for your feedback! 🙏", "entry": entry}

@router.get("/feedback")
async def get_feedback():
    feedbacks = get_all_feedback()
    return {
        "totalReviews": len(feedbacks),
        "averageRating": get_average_rating(),
        "feedbacks": feedbacks,
    }
