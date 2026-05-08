"""
ML Model 4 — Spaced Repetition Scheduler (SM-2 Algorithm)

Generates a scientifically-backed day-by-day study timetable using the
SuperMemo SM-2 spaced repetition algorithm, adapted for fixed exam deadlines.

The SM-2 algorithm calculates optimal review intervals based on memory
decay curves. Combined with topic importance weights, it ensures students
review high-priority material more frequently while still covering
everything before the exam.
"""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger("prepzo.spaced_repetition")


# ─────────────────────────────────────────────
# SM-2 Core Algorithm
# ─────────────────────────────────────────────

def _sm2_interval(repetition: int, ease_factor: float) -> int:
    """
    Calculate the next review interval using SM-2.

    repetition: number of successful reviews (0 = first learning)
    ease_factor: difficulty multiplier (1.3 minimum, 2.5 default)

    Returns: days until next review
    """
    if repetition == 0:
        return 1  # Review next day
    elif repetition == 1:
        return 3  # Review in 3 days
    else:
        prev = _sm2_interval(repetition - 1, ease_factor)
        return max(1, round(prev * ease_factor))


# ─────────────────────────────────────────────
# Mode Configurations
# ─────────────────────────────────────────────

_MODE_CONFIG = {
    "survival": {
        "hours_per_day": 8,
        "learn_minutes": 30,
        "review_minutes": 15,
        "practice_minutes": 20,
        "max_new_per_day_ratio": 1.0,  # Learn everything ASAP
    },
    "balanced": {
        "hours_per_day": 5,
        "learn_minutes": 45,
        "review_minutes": 20,
        "practice_minutes": 30,
        "max_new_per_day_ratio": 0.33,
    },
    "full": {
        "hours_per_day": 4,
        "learn_minutes": 60,
        "review_minutes": 25,
        "practice_minutes": 40,
        "max_new_per_day_ratio": 0.20,
    },
}

_TIPS = {
    "survival": [
        "🔥 Focus on must-do topics only. Skip optional material.",
        "⚡ Use active recall: close notes and test yourself.",
        "🎯 Practice writing answers under time pressure.",
    ],
    "balanced": [
        "📝 Start with the hardest topics while your mind is fresh.",
        "🔄 Review yesterday's topics before starting new ones.",
        "💡 Create mind maps to connect related concepts.",
        "✍️ Practice writing full exam-style answers.",
        "🧠 Teach a concept out loud to test your understanding.",
    ],
    "full": [
        "📚 Deep-dive into fundamentals before advanced topics.",
        "🔄 Space your reviews — don't cram everything in one day.",
        "🎯 Practice past paper questions under timed conditions.",
        "💡 Build connections between topics for deeper understanding.",
        "📝 Write summary notes in your own words.",
        "🧪 Try solving problems without looking at solutions first.",
        "🔍 Focus on edge cases and common exam traps.",
    ],
}


# ─────────────────────────────────────────────
# Public: Generate Study Schedule
# ─────────────────────────────────────────────

def generate_study_schedule(
    topics: list,
    exam_date: str,
    mode: str,
    weights: dict = None,
) -> list:
    """
    Generate a day-by-day study schedule using SM-2 spaced repetition.

    Args:
        topics: List of topic strings
        exam_date: ISO date string (YYYY-MM-DD)
        mode: survival | balanced | full
        weights: Topic importance weights from TF-IDF

    Returns:
        list of day objects:
        [
            {
                "day": 1,
                "date": "2026-05-10",
                "label": "Day 1",
                "topics": [
                    {
                        "name": "Arrays",
                        "action": "learn",    # learn | review | practice
                        "duration_minutes": 45,
                        "priority": "high"
                    }
                ],
                "totalMinutes": 120,
                "tip": "Focus on understanding core concepts first."
            }
        ]
    """
    try:
        exam_dt = datetime.strptime(exam_date, "%Y-%m-%d")
    except ValueError:
        return []

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    days_left = max(1, (exam_dt - today).days)

    if not topics:
        return []

    cfg = _MODE_CONFIG.get(mode, _MODE_CONFIG["balanced"])
    max_minutes = cfg["hours_per_day"] * 60
    max_new_per_day = max(1, round(len(topics) * cfg["max_new_per_day_ratio"]))
    mode_tips = _TIPS.get(mode, _TIPS["balanced"])

    # Sort topics by importance
    if weights:
        sorted_topics = sorted(topics, key=lambda t: -weights.get(t, 0.5))
    else:
        sorted_topics = list(topics)

    # Assign ease factors: high importance → lower ease → more frequent review
    ease_factors = {}
    for t in sorted_topics:
        w = weights.get(t, 0.5) if weights else 0.5
        ease_factors[t] = max(1.3, 2.5 - (w * 1.2))

    # Track each topic's learning state
    topic_state = {
        t: {
            "learned": False,
            "repetitions": 0,
            "next_review": None,
            "ease": ease_factors.get(t, 2.0),
        }
        for t in sorted_topics
    }

    topics_queue = list(sorted_topics)  # Topics not yet introduced
    schedule = []

    for day_num in range(1, days_left + 1):
        current_date = today + timedelta(days=day_num)
        is_last_day = day_num == days_left
        day_topics = []
        remaining = max_minutes

        # ── Phase 1: Scheduled SM-2 Reviews ──
        for t in sorted_topics:
            state = topic_state[t]
            if not state["learned"] or not state["next_review"]:
                continue
            if state["next_review"] > current_date:
                continue

            action = "review" if state["repetitions"] < 3 else "practice"
            mins = cfg["review_minutes"] if action == "review" else cfg["practice_minutes"]

            if remaining < mins:
                break

            w = weights.get(t, 0.5) if weights else 0.5
            priority = "high" if w >= 0.7 else "medium" if w >= 0.4 else "low"

            day_topics.append(
                {
                    "name": t,
                    "action": action,
                    "duration_minutes": mins,
                    "priority": priority,
                }
            )
            remaining -= mins

            # Advance SM-2 state
            state["repetitions"] += 1
            interval = _sm2_interval(state["repetitions"], state["ease"])
            state["next_review"] = current_date + timedelta(days=interval)

        # ── Phase 2: Introduce New Topics ──
        if not is_last_day:
            new_count = 0
            while (
                topics_queue
                and new_count < max_new_per_day
                and remaining >= cfg["learn_minutes"]
            ):
                t = topics_queue.pop(0)
                w = weights.get(t, 0.5) if weights else 0.5
                priority = "high" if w >= 0.7 else "medium" if w >= 0.4 else "low"

                day_topics.append(
                    {
                        "name": t,
                        "action": "learn",
                        "duration_minutes": cfg["learn_minutes"],
                        "priority": priority,
                    }
                )
                remaining -= cfg["learn_minutes"]

                topic_state[t]["learned"] = True
                topic_state[t]["repetitions"] = 0
                topic_state[t]["next_review"] = current_date + timedelta(days=1)
                new_count += 1

        # ── Last Day: Everything becomes practice ──
        if is_last_day:
            for dt in day_topics:
                dt["action"] = "practice"

        if day_topics:
            tip = mode_tips[(day_num - 1) % len(mode_tips)]
            if is_last_day:
                tip = "🎯 Final day! Quick review of must-do topics, then rest well. Trust your preparation."

            schedule.append(
                {
                    "day": day_num,
                    "date": current_date.strftime("%Y-%m-%d"),
                    "label": f"Day {day_num}"
                    + (" (Exam Day)" if is_last_day else ""),
                    "topics": day_topics,
                    "totalMinutes": sum(d["duration_minutes"] for d in day_topics),
                    "tip": tip,
                }
            )

    logger.info(
        "[SM-2] Generated %d-day schedule for %d topics (mode=%s, days_left=%d)",
        len(schedule),
        len(sorted_topics),
        mode,
        days_left,
    )
    return schedule
