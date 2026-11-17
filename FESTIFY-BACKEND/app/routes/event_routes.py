
from flask import Blueprint, request, jsonify, g

from app.extensions import db
from app.models.event import Event
from app.models.organizer_profile import OrganizerProfile
from app.models.venue import Venue

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.event_service import (
    create_event,
    get_all_events,
    get_event_by_id,
    event_to_dict,
    update_event,
    submit_event,
    approve_event,
    reject_event,
    publish_event,
    cancel_event,
    complete_event,
    delete_event,
    increment_attendance,
    add_custom_field,
    update_custom_field,
    delete_custom_field,
    get_custom_fields_for_event,
    get_published_events,
)

event_bp = Blueprint("event", __name__)


def current_organizer():
    """Resolve the organizer profile belonging to the authenticated user."""
    user_id = g.user.get("user_id")

    if not user_id:
        return None

    return OrganizerProfile.query.filter_by(user_id=user_id).first()


def organizer_error(profile):
    if not profile:
        return jsonify({
            "success": False,
            "message": "Organizer profile not found"
        }), 404

    if profile.organizer_status != "APPROVED":
        return jsonify({
            "success": False,
            "message": "Organizer profile is awaiting admin approval"
        }), 403

    return None


# ---------------------------------------------------------
# PUBLIC STUDENT EVENT DISCOVERY
# ---------------------------------------------------------

@event_bp.route("/published", methods=["GET"])
def published_events_route():
    result, status_code = get_published_events(
        category=request.args.get("category"),
        society=request.args.get("society"),
        event_date=request.args.get("event_date"),
    )
    return jsonify(result), status_code

@event_bp.route("/lineup", methods=["GET"])
def event_lineup_route():
    rows = (
        db.session.query(Event, Venue.venue_name)
        .outerjoin(Venue, Event.venue_id == Venue.venue_id)
        .filter(Event.status.in_(["APPROVED", "PUBLISHED"]))
        .order_by(Event.event_date.asc(), Event.start_time.asc())
        .all()
    )

    event_list = []

    for event, venue_name in rows:
        event_data = event_to_dict(event)
        event_data["venue_name"] = venue_name
        event_list.append(event_data)

    return jsonify({
        "success": True,
        "events": event_list,
    }), 200
# ---------------------------------------------------------
# ORGANIZER: CREATE EVENT
# ---------------------------------------------------------

@event_bp.route("/", methods=["POST"])
@token_required
@roles_required("ORGANIZER")
def create_event_route():
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    data = request.get_json(silent=True) or {}
    data["organizer_id"] = profile.organizer_id

    result, status_code = create_event(data)
    return jsonify(result), status_code


# ---------------------------------------------------------
# LIST EVENTS
# Admin: all events
# Organizer: own events only
# ---------------------------------------------------------

@event_bp.route("/", methods=["GET"])
@token_required
@roles_required("ORGANIZER", "ADMIN")
def get_events_route():
    if g.user.get("role") == "ADMIN":
        result, status_code = get_all_events(
            request.args.get("status")
        )
        return jsonify(result), status_code

    profile = current_organizer()
    if not profile:
        return jsonify({
            "success": False,
            "message": "Organizer profile not found"
        }), 404

    query = Event.query.filter_by(
        organizer_id=profile.organizer_id
    )

    status_filter = request.args.get("status")
    if status_filter:
        query = query.filter_by(status=status_filter.upper())

    events = query.order_by(
        Event.date_created.desc()
    ).all()

    return jsonify({
        "success": True,
        "events": [event_to_dict(e) for e in events]
    }), 200


# ---------------------------------------------------------
# GET EVENT DETAILS
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>", methods=["GET"])
@token_required
def get_event_route(event_id):
    return get_event_by_id(event_id)


# ---------------------------------------------------------
# UPDATE EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>", methods=["PUT"])
@token_required
@roles_required("ORGANIZER")
def update_event_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    data = request.get_json(silent=True) or {}
    data.pop("organizer_id", None)

    result, status_code = update_event(
        event_id,
        profile.organizer_id,
        data
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# DELETE DRAFT EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>", methods=["DELETE"])
@token_required
@roles_required("ORGANIZER")
def delete_event_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    result, status_code = delete_event(
        event_id,
        profile.organizer_id
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# SUBMIT EVENT FOR ADMIN APPROVAL
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/submit", methods=["POST"])
@token_required
@roles_required("ORGANIZER")
def submit_event_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    result, status_code = submit_event(
        event_id,
        profile.organizer_id
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# ADMIN: APPROVE EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/approve", methods=["PATCH"])
@token_required
@roles_required("ADMIN")
def approve_event_route(event_id):
    result, status_code = approve_event(event_id)
    return jsonify(result), status_code


# ---------------------------------------------------------
# ADMIN: REJECT EVENT WITH REMARK
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/reject", methods=["PATCH"])
@token_required
@roles_required("ADMIN")
def reject_event_route(event_id):
    data = request.get_json(silent=True) or {}
    reason = data.get("rejection_reason", "").strip()

    if not reason:
        return jsonify({
            "success": False,
            "message": "Rejection remark is required"
        }), 400

    result, status_code = reject_event(event_id, reason)
    return jsonify(result), status_code


# ---------------------------------------------------------
# ORGANIZER: PUBLISH APPROVED EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/publish", methods=["PATCH"])
@token_required
@roles_required("ORGANIZER")
def publish_event_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    result, status_code = publish_event(
        event_id,
        profile.organizer_id
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# ORGANIZER: CANCEL EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/cancel", methods=["PATCH"])
@token_required
@roles_required("ORGANIZER")
def cancel_event_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    result, status_code = cancel_event(
        event_id,
        profile.organizer_id
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# ADMIN: COMPLETE EVENT
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/complete", methods=["PATCH"])
@token_required
@roles_required("ADMIN")
def complete_event_route(event_id):
    result, status_code = complete_event(event_id)
    return jsonify(result), status_code


# ---------------------------------------------------------
# RECORD ATTENDANCE
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/attend", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def attend_event_route(event_id):
    result, status_code = increment_attendance(event_id)
    return jsonify(result), status_code


# ---------------------------------------------------------
# ORGANIZER: ADD CUSTOM REGISTRATION FIELD
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/fields", methods=["POST"])
@token_required
@roles_required("ORGANIZER")
def add_custom_field_route(event_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    data = request.get_json(silent=True) or {}

    result, status_code = add_custom_field(
        event_id,
        profile.organizer_id,
        data
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# GET CUSTOM FIELDS
# ---------------------------------------------------------

@event_bp.route("/<int:event_id>/fields", methods=["GET"])
@token_required
def get_custom_fields_route(event_id):
    return get_custom_fields_for_event(event_id)


# ---------------------------------------------------------
# ORGANIZER: UPDATE CUSTOM FIELD
# ---------------------------------------------------------

@event_bp.route("/fields/<int:custom_field_id>", methods=["PUT"])
@token_required
@roles_required("ORGANIZER")
def update_custom_field_route(custom_field_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    data = request.get_json(silent=True) or {}

    result, status_code = update_custom_field(
        custom_field_id,
        profile.organizer_id,
        data
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# ORGANIZER: DELETE CUSTOM FIELD
# ---------------------------------------------------------

@event_bp.route("/fields/<int:custom_field_id>", methods=["DELETE"])
@token_required
@roles_required("ORGANIZER")
def delete_custom_field_route(custom_field_id):
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    result, status_code = delete_custom_field(
        custom_field_id,
        profile.organizer_id
    )
    return jsonify(result), status_code


# ---------------------------------------------------------
# ORGANIZER: ACTIVE VENUES FOR EVENT FORM
# ---------------------------------------------------------

@event_bp.route("/venues", methods=["GET"])
@token_required
@roles_required("ORGANIZER")
def list_venues_route():
    profile = current_organizer()
    error = organizer_error(profile)

    if error:
        return error

    venues = Venue.query.filter_by(
        venue_status="ACTIVE"
    ).order_by(Venue.venue_name.asc()).all()

    return jsonify({
        "success": True,
        "venues": [
            {
                "venue_id": venue.venue_id,
                "venue_name": venue.venue_name,
                "location": venue.location,
                "capacity": venue.capacity,
                "description": venue.description
            }
            for venue in venues
        ]
    }), 200
