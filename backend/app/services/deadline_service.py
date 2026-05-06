from datetime import datetime

def calculate_deadline_mode(exam_date_str: str) -> str:
    """
    Calculates the deadline mode based on the exam date.
    <= 3 days -> survival
    4-7 days -> balanced
    > 7 days -> full
    """
    try:
        # Assuming format YYYY-MM-DD
        exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d")
        today = datetime.now()
        days_left = (exam_date - today).days
        
        if days_left <= 3:
            return "survival"
        elif 4 <= days_left <= 7:
            return "balanced"
        else:
            return "full"
    except ValueError:
        # Default fallback if date parsing fails
        return "balanced"
