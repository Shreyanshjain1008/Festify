from flask import Blueprint, request

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.society_service import (
    create_society,
    get_all_societies,
    get_society_by_id,
    update_society
)


society_bp = Blueprint(
    "society",
    __name__
)


# =========================================================
# REGISTER SOCIETY
# =========================================================

@society_bp.route("/", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def create():

    data = request.get_json(silent=True)

    if not data:

        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return create_society(data)


# =========================================================
# GET ALL SOCIETIES
# ADMIN ONLY
# =========================================================

@society_bp.route(
    "/",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_all():

    return get_all_societies()


# =========================================================
# GET SOCIETY BY ID
# =========================================================

@society_bp.route(
    "/<int:society_id>",
    methods=["GET"]
)
@token_required
@roles_required("ADMIN")
def get_one(society_id):

    return get_society_by_id(
        society_id
    )


# =========================================================
# UPDATE SOCIETY
# =========================================================

@society_bp.route(
    "/<int:society_id>",
    methods=["PUT"]
)
@token_required
@roles_required("ADMIN")
def update(society_id):

    data = request.get_json(silent=True)

    if not data:

        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_society(
        society_id,
        data
    )