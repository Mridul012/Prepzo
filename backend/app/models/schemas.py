from pydantic import BaseModel
from typing import List, Optional

class GeneratePlanRequest(BaseModel):
    subject: str
    examDate: str
    topics: List[str]
    pdfText: Optional[str] = None

class Question(BaseModel):
    question: str
    type: str  # MCQ | coding | theory
    difficulty: str  # easy | medium | hard
    probability: float
    priority: str  # must | should | optional
    solution: str

class GeneratePlanResponse(BaseModel):
    mode: str
    strategy: str
    questions: List[Question]
