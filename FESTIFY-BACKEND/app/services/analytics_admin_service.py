from app.extensions import db
from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.feedback import Feedback
from app.models.user import User
from app.models.society import Society
from app.models.organizer_profile import OrganizerProfile


def get_admin_analytics():
    events_by_status = {s: Event.query.filter_by(status=s).count() for s in
                         ["DRAFT", "PENDING", "APPROVED", "REJECTED", "PUBLISHED", "COMPLETED", "CANCELLED"]}
    societies_by_status = {s: Society.query.filter_by(status=s).count() for s in
                            ["PENDING", "APPROVED", "REJECTED", "INACTIVE"]}
    organizers_by_status = {s: OrganizerProfile.query.filter_by(organizer_status=s).count() for s in
                             ["PENDING", "APPROVED", "REJECTED", "INACTIVE"]}

    feedback_entries = Feedback.query.all()
    total_feedback = len(feedback_entries)
    average_rating = round(sum(f.rating for f in feedback_entries) / total_feedback, 2) if total_feedback else 0
    feedback_by_event = {}
    for event in Event.query.all():
        entries = [f for f in feedback_entries if f.event_id == event.event_id]
        feedback_by_event[str(event.event_id)] = {
            "event_name": event.event_name,
            "feedback_count": len(entries),
            "average_rating": round(sum(f.rating for f in entries) / len(entries), 2) if entries else 0,
            "rating_distribution": {str(star): sum(1 for f in entries if f.rating == star) for star in range(1, 6)},
        }

    return {"success": True, "analytics": {
        "total_participants": User.query.filter_by(role="PARTICIPANT").count(),
        "total_organizers": User.query.filter_by(role="ORGANIZER").count(),
        "total_societies": Society.query.count(),
        "total_events": Event.query.count(),
        "total_registrations": EventRegistration.query.filter_by(registration_status="CONFIRMED").count(),
        "events_by_status": events_by_status,
        "total_attendance": db.session.query(db.func.sum(Event.attendance_count)).scalar() or 0,
        "total_feedback_count": total_feedback,
        "average_rating": average_rating,
        "feedback_by_event": feedback_by_event,
        "societies_by_status": societies_by_status,
        "organizers_by_status": organizers_by_status,
    }}, 200