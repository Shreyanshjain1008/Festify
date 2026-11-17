from flask import Blueprint, request, g, Response

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.pass_service import (
    issue_pass,
    get_pass_by_id,
    validate_pass_by_id,
    cancel_pass,
    get_user_passes,
    render_pass_page
)


pass_bp = Blueprint("pass", __name__)


# =========================================================
# ISSUE FEST PASS
# PARTICIPANT ONLY
# =========================================================

@pass_bp.route("/", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def issue_pass_route():

    data = request.get_json(silent=True) or {}

    if "fest_date" not in data:
        return {
            "success": False,
            "message": "fest_date is required"
        }, 400

    user_id = g.user["user_id"]

    return issue_pass(
        user_id,
        data["fest_date"]
    )


# =========================================================
# GET PASS
# AUTHENTICATED USER
# =========================================================

@pass_bp.route("/<int:fest_pass_id>", methods=["GET"])
@token_required
def get_pass_route(fest_pass_id):

    return get_pass_by_id(fest_pass_id)


# =========================================================
# VALIDATE PASS
# ADMIN ONLY
# =========================================================

@pass_bp.route(
    "/<int:fest_pass_id>/validate",
    methods=["POST"]
)
@token_required
@roles_required("ADMIN")
def validate_pass_route(fest_pass_id):

    return validate_pass_by_id(fest_pass_id)


# =========================================================
# CANCEL PASS
# PARTICIPANT ONLY
# =========================================================

@pass_bp.route(
    "/<int:fest_pass_id>/cancel",
    methods=["PATCH"]
)
@token_required
@roles_required("PARTICIPANT")
def cancel_pass_route(fest_pass_id):

    user_id = g.user["user_id"]

    return cancel_pass(
        fest_pass_id,
        user_id
    )


# =========================================================
# GET USER PASSES
# PARTICIPANT / ADMIN
# =========================================================

@pass_bp.route(
    "/users/<int:user_id>",
    methods=["GET"]
)
@token_required
@roles_required("PARTICIPANT", "ADMIN")
def get_user_passes_route(user_id):

    return get_user_passes(user_id)

@token_required
@pass_bp.route("/verify/<token>", methods=["GET"])
def verify_pass_page(token):
    return Response(render_pass_page(token), mimetype="text/html")