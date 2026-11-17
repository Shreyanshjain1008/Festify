from flask import Blueprint, request, g, jsonify

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required
from app.extensions import db
from app.models.feedback import Feedback
from app.models.event_reaction import EventReaction
from app.models.event import Event
from app.services.feedback_service import (
    create_feedback, get_all_feedback, get_feedback_by_id,
    update_feedback, delete_feedback,
)

feedback_bp = Blueprint("feedback", __name__)

def _jwt_user_id():
    """Get user ID from the verified JWT token."""
    claims = g.get("user") or {}
    value = claims.get("user_id") or claims.get("id") or claims.get("sub")

    if value in (None, ""):
        return None

    try:
        return int(value)
    except (TypeError, ValueError):
        return None
def _jwt_user_id():
    """Read the user identifier only from the already-verified JWT payload."""
    claims = g.get("user") or {}
    value = claims.get("user_id") or claims.get("id") or claims.get("sub")
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


@feedback_bp.route("/reactions", methods=["GET"])
@token_required
@roles_required("PARTICIPANT", "ORGANIZER", "ADMIN", "SUPER_ADMIN")
def get_reactions():
    raw_ids = request.args.get("event_ids", "")
    try:
        event_ids = [int(value) for value in raw_ids.split(",") if value.strip()]
    except ValueError:
        return jsonify({"success": False, "message": "event_ids must be comma-separated integers"}), 400
    if not event_ids:
        return jsonify({"success": True, "reactions": {}}), 200
    rows = EventReaction.query.filter(EventReaction.event_id.in_(event_ids)).all()
    current_user_id = _jwt_user_id()
    result = {}
    for event_id in event_ids:
        selected = [row for row in rows if row.event_id == event_id]
        result[str(event_id)] = {
            "likes": sum(1 for row in selected if row.reaction == "LIKE"),
            "dislikes": sum(1 for row in selected if row.reaction == "DISLIKE"),
            "my_reaction": next((row.reaction.lower() for row in selected if row.user_id == current_user_id), None),
        }
    return jsonify({"success": True, "reactions": result}), 200


@feedback_bp.route("/reactions/<int:event_id>", methods=["PUT", "DELETE"])
@token_required
@roles_required("PARTICIPANT")
def set_reaction(event_id):
    user_id = _jwt_user_id()
    if user_id is None:
        return jsonify({"success": False, "message": "Your login token does not contain a valid user ID. Please log out and log in again."}), 401
    event = Event.query.get(event_id)
    if not event:
        return jsonify({"success": False, "message": "Event not found"}), 404
    existing = EventReaction.query.filter_by(event_id=event_id, user_id=user_id).first()
    if request.method == "DELETE":
        if existing:
            db.session.delete(existing)
            db.session.commit()
        return jsonify({"success": True, "message": "Reaction removed"}), 200
    data = request.get_json(silent=True) or {}
    reaction = data.get("reaction")
    if reaction not in ("like", "dislike"):
        return jsonify({"success": False, "message": "reaction must be 'like' or 'dislike'"}), 400
    try:
        if existing:
            existing.reaction = reaction.upper()
        else:
            db.session.add(EventReaction(user_id=user_id, event_id=event_id, reaction=reaction.upper()))
        db.session.commit()
        return jsonify({"success": True, "message": "Reaction saved", "reaction": reaction}), 200
    except Exception as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": "Could not save reaction", "error": str(exc)}), 500


@feedback_bp.route("/", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def create():
    data = request.get_json(silent=True) or {}

    if not data:
        return jsonify({
            "success": False,
            "message": "Request body is required"
        }), 400

    claims = g.get("user") or {}
    user_id = claims.get("user_id") or claims.get("id") or claims.get("sub")

    try:
        user_id = int(user_id)
    except (TypeError, ValueError):
        return jsonify({
            "success": False,
            "message": "Invalid user ID in authentication token"
        }), 401

    payload, status = create_feedback(data, authenticated_user_id=user_id)
    return jsonify(payload), status


@feedback_bp.route("/mine", methods=["GET"])
@token_required
@roles_required("PARTICIPANT")
def get_my_feedback():
    user_id = _jwt_user_id()
    if user_id is None:
        return jsonify({"success": False, "message": "Your login token does not contain a valid user ID."}), 401
    rows = Feedback.query.filter_by(user_id=user_id).order_by(Feedback.date_created.desc()).all()
    return jsonify({"success": True, "feedback": [
        {"feedback_id": row.feedback_id, "event_id": row.event_id, "rating": row.rating,
         "comment": row.comment, "date_created": row.date_created.isoformat() if row.date_created else None}
        for row in rows
    ]}), 200


@feedback_bp.route("/", methods=["GET"])
@token_required
@roles_required("ADMIN", "ORGANIZER")
def get_all():
    payload, status = get_all_feedback()
    return jsonify(payload), status


@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
@token_required
@roles_required("ADMIN", "ORGANIZER", "PARTICIPANT")
def get_one(feedback_id):
    owner_id = _jwt_user_id() if (g.user or {}).get("role") == "PARTICIPANT" else None
    payload, status = get_feedback_by_id(feedback_id, owner_id=owner_id)
    return jsonify(payload), status


@feedback_bp.route("/<int:feedback_id>", methods=["PUT"])
@token_required
@roles_required("PARTICIPANT")
def update(feedback_id):
    data = request.get_json(silent=True) or {}
    if not data:
        return jsonify({"success": False, "message": "Request body is required"}), 400
    payload, status = update_feedback(feedback_id, data, owner_id=_jwt_user_id())
    return jsonify(payload), status


@feedback_bp.route("/<int:feedback_id>", methods=["DELETE"])
@token_required
@roles_required("PARTICIPANT")
def delete(feedback_id):
    payload, status = delete_feedback(feedback_id, owner_id=_jwt_user_id())
    return jsonify(payload), status
