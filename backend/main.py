from fastapi import FastAPI
from app.routes import plan

app = FastAPI(
    title="Prepzo API",
    description="Deadline-Aware Exam Preparation Engine MVP",
    version="0.1.0"
)

app.include_router(plan.router, prefix="/api")

@app.get("/")
def read_root():
    return {"message": "Welcome to Prepzo API"}
