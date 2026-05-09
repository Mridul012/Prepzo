from typing import List

_feedbacks = []

def add_feedback(entry: dict):
    _feedbacks.append(entry)

def get_all_feedback() -> List[dict]:
    return _feedbacks

def get_average_rating() -> float:
    if not _feedbacks:
        return 0.0
    return round(sum(f["rating"] for f in _feedbacks) / len(_feedbacks), 2)
