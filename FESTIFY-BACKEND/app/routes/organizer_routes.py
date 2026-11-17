from flask import Blueprint, request, g

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.organizer_service import (
    create_organizer,
    get_all_organizers,
    get_organizer_by_id,
    update_organizer
)


organizer_bp = Blueprint("organizer", __name__)


# =========================================================
# CREATE ORGANIZER REQUEST
# PARTICIPANT ONLY
# =========================================================

@organizer_bp.route("/", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def create():

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    # user_id JWT se aayega
    data["user_id"] = g.user["user_id"]

    return create_organizer(data)


# =========================================================
# GET ALL ORGANIZERS
# ADMIN ONLY
# =========================================================

@organizer_bp.route("/", methods=["GET"])
@token_required
@roles_required("ADMIN")
def get_all():

    return get_all_organizers()


# =========================================================
# GET ORGANIZER BY ID
# ADMIN / ORGANIZER
# =========================================================

@organizer_bp.route("/<int:organizer_id>", methods=["GET"])
@token_required
@roles_required("ADMIN", "ORGANIZER")
def get_one(organizer_id):

    return get_organizer_by_id(organizer_id)


# =========================================================
# UPDATE ORGANIZER
# ADMIN / ORGANIZER
# =========================================================

@organizer_bp.route("/<int:organizer_id>", methods=["PUT"])
@token_required
@roles_required("ADMIN", "ORGANIZER")
def update(organizer_id):

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_organizer(
        organizer_id,
        data
    )