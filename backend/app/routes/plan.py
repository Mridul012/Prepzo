from fastapi import APIRouter
from app.models.schemas import GeneratePlanRequest, GeneratePlanResponse, Question
from app.services.deadline_service import calculate_deadline_mode

router = APIRouter()

@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    # Calculate mode based on exam deadline
    mode = calculate_deadline_mode(request.examDate)
    
    # Dummy response for STEP 3
    dummy_question = Question(
        question="What is FastAPI?",
        type="theory",
        difficulty="easy",
        probability=0.95,
        priority="must",
        solution="FastAPI is a modern, fast (high-performance), web framework for building APIs with Python 3.8+ based on standard Python type hints."
    )
    
    return GeneratePlanResponse(
        mode=mode,
        strategy=f"You are in {mode.upper()} mode based on your exam date. Focus on these priority questions.",
        questions=[dummy_question]
    )
