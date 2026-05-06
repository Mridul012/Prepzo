import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Initialize Groq client
api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key) if api_key and api_key != "your_groq_api_key_here" else None

def generate_questions_from_llm(subject: str, topics: list, mode: str, pdf_text: str = None) -> list:
    """
    Calls the Groq API to generate high-probability questions based on the exam context.
    """
    if not client:
        # Fallback for development if no valid API key is provided
        return [
            {
                "question": f"Explain the core principles of {subject} focusing on {topics[0] if topics else 'the basics'}.",
                "type": "theory",
                "difficulty": "medium",
                "probability": 0.85,
                "priority": "must",
                "solution": "This is a dummy solution generated because Groq API key is missing."
            }
        ]

    prompt = f"""
    You are an AI Exam Preparation Engine.
    Subject: {subject}
    Topics: {', '.join(topics)}
    Mode: {mode} (Survival=<=3 days, Balanced=4-7 days, Full=>7 days)
    
    Generate 2 high-probability exam questions based on the above.
    Return ONLY a JSON object with a key 'questions' which is an array of objects. 
    Each object must have: 
    - question (string)
    - type (string: "MCQ", "coding", or "theory")
    - difficulty (string: "easy", "medium", or "hard")
    - probability (float: 0.0 to 1.0)
    - priority (string: "must", "should", or "optional")
    - solution (string)
    """

    try:
        completion = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that outputs strict JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        data = json.loads(response_text)
        return data.get("questions", [])
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return []
