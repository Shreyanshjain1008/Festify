from datetime import date as date_cls

from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.feedback import Feedback
from app.models.event_reaction import EventReaction


def get_organizer_analytics(organizer_id):
    events = Event.query.filter_by(organizer_id=organizer_id).all()
    event_ids = [e.event_id for e in events]

    total_registrations = 0
    if event_ids:
        total_registrations = EventRegistration.query.filter(
            EventRegistration.event_id.in_(event_ids),
            EventRegistration.registration_status == "CONFIRMED"
        ).count()

    total_attendance = sum(e.attendance_count for e in events)
    total_capacity = sum(e.capacity for e in events)
    capacity_utilization = round((total_registrations / total_capacity) * 100, 2) if total_capacity else 0

    feedback_entries = Feedback.query.filter(Feedback.event_id.in_(event_ids)).all() if event_ids else []
    total_feedback = len(feedback_entries)
    average_rating = round(sum(f.rating for f in feedback_entries) / total_feedback, 2) if total_feedback else 0

    rating_distribution = {str(i): 0 for i in range(1, 6)}
    for f in feedback_entries:
        rating_distribution[str(f.rating)] += 1

    feedback_by_event = {}
    for event in events:
        event_feedback = [f for f in feedback_entries if f.event_id == event.event_id]
        feedback_by_event[str(event.event_id)] = {
            "event_name": event.event_name,
            "feedback_count": len(event_feedback),
            "average_rating": round(sum(f.rating for f in event_feedback) / len(event_feedback), 2) if event_feedback else 0,
            "rating_distribution": {
                str(star): sum(1 for f in event_feedback if f.rating == star)
                for star in range(1, 6)
            },
            "comments": [
                {"rating": f.rating, "comment": f.comment,
                 "user_name": f.user.name if f.user else "Student"}
                for f in event_feedback if f.comment
            ],
        }

    # Reactions are stored separately from 1–5 star feedback.
    reaction_entries = EventReaction.query.filter(EventReaction.event_id.in_(event_ids)).all() if event_ids else []
    reactions_by_event = {}
    for event in events:
        event_reactions = [r for r in reaction_entries if r.event_id == event.event_id]
        reactions_by_event[str(event.event_id)] = {
            "likes": sum(1 for r in event_reactions if r.reaction == "LIKE"),
            "dislikes": sum(1 for r in event_reactions if r.reaction == "DISLIKE"),
        }
    total_likes = sum(item["likes"] for item in reactions_by_event.values())
    total_dislikes = sum(item["dislikes"] for item in reactions_by_event.values())

    return {
        "total_events": len(events),
        "upcoming_events": len([e for e in events if e.event_date >= date_cls.today() and e.status == "PUBLISHED"]),
        "total_registrations": total_registrations,
        "total_attendance": total_attendance,
        "capacity_utilization_percent": capacity_utilization,
        "average_rating": average_rating,
        "total_feedback_count": total_feedback,
        "rating_distribution": rating_distribution,
        "feedback_by_event": feedback_by_event,
        "reactions_by_event": reactions_by_event,
        "total_likes": total_likes,
        "total_dislikes": total_dislikes,
    }