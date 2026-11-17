
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.feedback import Feedback
from app.models.event import Event


def feedback_to_dict(feedback):
    return {
        "feedback_id": feedback.feedback_id,
        "user_id": feedback.user_id,
        "event_id": feedback.event_id,
        "rating": feedback.rating,
        "comment": feedback.comment,
        "date_created": (
            feedback.date_created.isoformat()
            if feedback.date_created else None
        )
    }


def create_feedback(data, authenticated_user_id=None):

    if authenticated_user_id is None:
        return {
            "success": False,
            "message": "Authenticated user ID is missing"
        }, 401

    try:
        user_id = int(authenticated_user_id)
        event_id = int(data.get("event_id"))
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return {
            "success": False,
            "message": "Valid event_id and rating are required"
        }, 400

    if not 1 <= rating <= 5:
        return {
            "success": False,
            "message": "Rating must be between 1 and 5"
        }, 400

    try:
        event = db.session.get(Event, event_id)

        if not event:
            return {
                "success": False,
                "message": "Selected event was not found"
            }, 404

        existing = Feedback.query.filter_by(
            user_id=user_id,
            event_id=event_id
        ).first()

        if existing:
            return {
                "success": False,
                "message": "You have already submitted feedback for this event"
            }, 409

        comment = data.get("comment")

        feedback = Feedback(
            user_id=user_id,
            event_id=event_id,
            rating=rating,
            comment=(
                comment.strip()
                if isinstance(comment, str) and comment.strip()
                else None
            )
        )

        db.session.add(feedback)
        db.session.commit()

        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback.feedback_id,
            "feedback": feedback_to_dict(feedback)
        }, 201

    except IntegrityError:
        db.session.rollback()
        return {
            "success": False,
            "message": "Feedback could not be saved because of a database constraint"
        }, 400

    except Exception as exc:
        db.session.rollback()
        return {
            "success": False,
            "message": "Failed to submit feedback",
            "error": str(exc)
        }, 500


def get_all_feedback():
    try:
        rows = Feedback.query.order_by(
            Feedback.date_created.desc()
        ).all()

        return {
            "success": True,
            "feedback": [feedback_to_dict(row) for row in rows]
        }, 200

    except Exception as exc:
        return {
            "success": False,
            "message": "Failed to fetch feedback",
            "error": str(exc)
        }, 500


def get_feedback_by_id(feedback_id, owner_id=None):
    feedback = db.session.get(Feedback, feedback_id)

    if not feedback or (
        owner_id is not None and feedback.user_id != int(owner_id)
    ):
        return {
            "success": False,
            "message": "Feedback not found"
        }, 404

    return {
        "success": True,
        "feedback": feedback_to_dict(feedback)
    }, 200


def update_feedback(feedback_id, data, owner_id=None):
    feedback = db.session.get(Feedback, feedback_id)

    if not feedback or (
        owner_id is not None and feedback.user_id != int(owner_id)
    ):
        return {
            "success": False,
            "message": "Feedback not found"
        }, 404

    if "rating" in data:
        try:
            rating = int(data["rating"])
        except (TypeError, ValueError):
            return {
                "success": False,
                "message": "Rating must be between 1 and 5"
            }, 400

        if not 1 <= rating <= 5:
            return {
                "success": False,
                "message": "Rating must be between 1 and 5"
            }, 400

        feedback.rating = rating

    if "comment" in data:
        feedback.comment = data["comment"]

    try:
        db.session.commit()
        return {
            "success": True,
            "message": "Feedback updated successfully"
        }, 200

    except Exception as exc:
        db.session.rollback()
        return {
            "success": False,
            "message": "Failed to update feedback",
            "error": str(exc)
        }, 500


def delete_feedback(feedback_id, owner_id=None):
    feedback = db.session.get(Feedback, feedback_id)

    if not feedback or (
        owner_id is not None and feedback.user_id != int(owner_id)
    ):
        return {
            "success": False,
            "message": "Feedback not found"
        }, 404

    try:
        db.session.delete(feedback)
        db.session.commit()

        return {
            "success": True,
            "message": "Feedback deleted successfully"
        }, 200

    except Exception as exc:
        db.session.rollback()
        return {
            "success": False,
            "message": "Failed to delete feedback",
            "error": str(exc)
        }, 500
