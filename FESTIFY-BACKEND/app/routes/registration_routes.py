from flask import Blueprint, request, jsonify, g
from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required
from app.services.registration_service import register_for_event, cancel_registration, get_registrations_for_event, get_registrations_for_user, registration_to_dict

registration_bp = Blueprint("registration", __name__)


@registration_bp.route("/events/<int:event_id>/register", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def register_route(event_id):
    data = request.get_json(silent=True) or {}
    success, message, registration = register_for_event(
        event_id,
        g.user["user_id"],
        data.get("custom_field_values", {}),
        data.get("event_day"),
    )
    if not success:
        status = 409 if registration is not None else 400
        payload = {"success": False, "message": message}
        if registration is not None:
            payload["registration"] = registration_to_dict(registration)
        return jsonify(payload), status
    return jsonify({
        "success": True,
        "message": message,
        "registration": registration_to_dict(registration, include_custom_values=True),
    }), 201


@registration_bp.route("/<int:registration_id>/cancel", methods=["PATCH"])
@token_required
@roles_required("PARTICIPANT")
def cancel_registration_route(registration_id):
    result, status = cancel_registration(registration_id, g.user["user_id"])
    return jsonify(result), status


@registration_bp.route("/events/<int:event_id>", methods=["GET"])
@token_required
@roles_required("ORGANIZER", "ADMIN")
def get_event_registrations_route(event_id):
    result, status = get_registrations_for_event(event_id)
    return jsonify(result), status


@registration_bp.route("/users/<int:user_id>", methods=["GET"])
@token_required
@roles_required("PARTICIPANT", "ADMIN")
def get_user_registrations_route(user_id):
    if g.user.get("role") != "ADMIN" and int(g.user.get("user_id")) != int(user_id):
        return jsonify({"success": False, "message": "You can only view your own registrations."}), 403
    result, status = get_registrations_for_user(user_id)
    return jsonify(result), status
