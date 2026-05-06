from fastapi import APIRouter

router = APIRouter()

# In-memory store for MVP analytics
analytics_data = {
    "users_count": 0,
    "plans_generated": 0,
    "avg_q_per_user": 0,
    "chat_msgs": 0
}

@router.get("/analytics")
async def get_analytics():
    """
    Returns platform analytics.
    """
    return analytics_data

@router.post("/analytics/track")
async def track_event(event_type: str):
    """
    Tracks an event (e.g., plan_generated, chat_msg_sent).
    """
    if event_type == "plan_generated":
        analytics_data["plans_generated"] += 1
    elif event_type == "chat_msg_sent":
        analytics_data["chat_msgs"] += 1
    elif event_type == "user_registered":
        analytics_data["users_count"] += 1
        
    return {"status": "success", "event": event_type}
