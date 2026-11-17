from flask import Blueprint, request

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.admin_service import (
    get_all_users_for_admin,
    update_user_status_by_admin,
    delete_user_by_admin,

    get_all_societies_for_admin,
    create_approved_society,
    update_society_by_admin,
    approve_society,
    reject_society,
    update_society_status,

    get_all_organizers_for_admin,
    approve_organizer,
    reject_organizer,
    update_organizer_status,

    get_all_events_for_admin,
    approve_event_by_admin,
    reject_event_by_admin,

    add_venue,
    update_venue_by_admin,
    disable_venue
)


admin_bp = Blueprint(
    "admin",
    __name__
)


# =========================================================
# USER MANAGEMENT
# =========================================================

@admin_bp.route(
    "/users",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_users():

    return get_all_users_for_admin()


@admin_bp.route(
    "/users/<int:user_id>/status",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def update_user_status(user_id):

    data = request.get_json(silent=True)

    if not data or "account_status" not in data:
        return {
            "success": False,
            "message": "account_status is required"
        }, 400

    return update_user_status_by_admin(
        user_id,
        data["account_status"]
    )


@admin_bp.route(
    "/users/<int:user_id>",
    methods=["DELETE"]
)
@token_required
@roles_required("ADMIN")
def delete_user(user_id):

    return delete_user_by_admin(
        user_id
    )


# =========================================================
# SOCIETY MANAGEMENT
# =========================================================

@admin_bp.route(
    "/societies",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_societies():

    return get_all_societies_for_admin()


@admin_bp.route("/societies", methods=["POST"])
@token_required
@roles_required("ADMIN")
def create_society_route():
    data = request.get_json(silent=True) or {}
    return create_approved_society(data)


@admin_bp.route("/societies/<int:society_id>", methods=["PUT", "PATCH"])
@token_required
@roles_required("ADMIN")
def update_society_route(society_id):
    data = request.get_json(silent=True) or {}
    return update_society_by_admin(society_id, data)


@admin_bp.route(
    "/societies/<int:society_id>/approve",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def approve_society_route(society_id):

    return approve_society(
        society_id
    )


@admin_bp.route(
    "/societies/<int:society_id>/reject",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def reject_society_route(society_id):

    data = request.get_json(silent=True) or {}

    return reject_society(
        society_id,
        data.get("rejection_reason")
    )


@admin_bp.route(
    "/societies/<int:society_id>/status",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def update_society_status_route(society_id):

    data = request.get_json(silent=True)

    if not data or "status" not in data:
        return {
            "success": False,
            "message": "status is required"
        }, 400

    return update_society_status(
        society_id,
        data["status"]
    )


# =========================================================
# ORGANIZER MANAGEMENT
# =========================================================

@admin_bp.route(
    "/organizers",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_organizers():

    return get_all_organizers_for_admin()


@admin_bp.route(
    "/organizers/<int:organizer_id>/approve",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def approve_organizer_route(organizer_id):

    return approve_organizer(
        organizer_id
    )


@admin_bp.route(
    "/organizers/<int:organizer_id>/reject",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def reject_organizer_route(organizer_id):

    data = request.get_json(silent=True) or {}

    return reject_organizer(
        organizer_id,
        data.get("rejection_reason")
    )


@admin_bp.route(
    "/organizers/<int:organizer_id>/status",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def update_organizer_status_route(organizer_id):

    data = request.get_json(silent=True)

    if not data or "status" not in data:
        return {
            "success": False,
            "message": "status is required"
        }, 400

    return update_organizer_status(
        organizer_id,
        data["status"]
    )


# =========================================================
# EVENT MANAGEMENT
# =========================================================

@admin_bp.route(
    "/events",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_events():

    return get_all_events_for_admin()


@admin_bp.route(
    "/events/<int:event_id>/approve",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def approve_event_route(event_id):

    return approve_event_by_admin(
        event_id
    )


@admin_bp.route(
    "/events/<int:event_id>/reject",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def reject_event_route(event_id):

    data = request.get_json(silent=True) or {}

    return reject_event_by_admin(
        event_id,
        data.get("rejection_reason")
    )


# =========================================================
# VENUE MANAGEMENT
# =========================================================

@admin_bp.route(
    "/venues",
    methods=["POST"]
)
@token_required
@roles_required("ADMIN")
def create_venue():

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return add_venue(data)


@admin_bp.route(
    "/venues/<int:venue_id>",
    methods=["PUT"]
)
@token_required
@roles_required("ADMIN")
def update_venue(venue_id):

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_venue_by_admin(
        venue_id,
        data
    )


@admin_bp.route(
    "/venues/<int:venue_id>/disable",
    methods=["PATCH"]
)
@token_required
@roles_required("ADMIN")
def disable_venue_route(venue_id):

    return disable_venue(
        venue_id
    )