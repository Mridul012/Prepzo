from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    context: str = None  # Could be a question ID or topic

@router.post("/chat")
async def chat_with_bot(request: ChatRequest):
    """
    Chatbot endpoint for doubts and explanations.
    """
    # Simple dummy response for MVP
    response_msg = f"This is an AI response to your message: '{request.message}'. "
    if request.context:
        response_msg += f"Context considered: {request.context}."
        
    return {
        "reply": response_msg
    }
