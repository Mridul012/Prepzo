from fastapi import APIRouter
from app.models.schemas import GeneratePlanRequest, GeneratePlanResponse, Question
from app.services.deadline_service import calculate_deadline_mode
from app.services.groq_service import generate_questions_from_llm

router = APIRouter()

@router.post("/generate-plan", response_model=GeneratePlanResponse)
async def generate_plan(request: GeneratePlanRequest):
    # Calculate mode based on exam deadline
    mode = calculate_deadline_mode(request.examDate)
    
    # STEP 4: Call Groq API to generate questions
    raw_questions = generate_questions_from_llm(
        subject=request.subject,
        topics=request.topics,
        mode=mode,
        pdf_text=request.pdfText
    )
    
    # Parse dicts to Question Pydantic models
    questions = []
    for q in raw_questions:
        try:
            questions.append(Question(**q))
        except Exception as e:
            print(f"Error parsing question: {e}")
            pass
    
    return GeneratePlanResponse(
        mode=mode,
        strategy=f"You are in {mode.upper()} mode based on your exam date. Focus on these {len(questions)} priority questions.",
        questions=questions
    )
