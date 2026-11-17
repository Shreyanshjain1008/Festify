
from flask import Blueprint, request

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.venue_service import (
    create_venue,
    get_all_venues,
    get_active_venues,
    get_venue_by_id,
    update_venue,
    delete_venue
)

venue_bp = Blueprint("venue", __name__)


# Organizer: load venues for the event form.
# Keep this route before /<int:venue_id>.
@venue_bp.route("/active", methods=["GET"])
@token_required
@roles_required("ORGANIZER")
def get_active():
    return get_active_venues()


# Admin: venue management.
@venue_bp.route("/", methods=["POST"])
@token_required
@roles_required("ADMIN")
def create():
    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return create_venue(data)


@venue_bp.route("/", methods=["GET"])
@token_required
@roles_required("ADMIN")
def get_all():
    return get_all_venues()


@venue_bp.route("/<int:venue_id>", methods=["GET"])
@token_required
@roles_required("ADMIN")
def get_one(venue_id):
    return get_venue_by_id(venue_id)


@venue_bp.route("/<int:venue_id>", methods=["PUT"])
@token_required
@roles_required("ADMIN")
def update(venue_id):
    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_venue(venue_id, data)


@venue_bp.route("/<int:venue_id>", methods=["DELETE"])
@token_required
@roles_required("ADMIN")
def delete(venue_id):
    return delete_venue(venue_id)
