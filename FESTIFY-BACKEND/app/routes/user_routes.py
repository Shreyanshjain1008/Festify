from flask import Blueprint, request, g

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.user_service import (
    get_all_users,
    get_user_by_id,
    update_user,
    update_user_status as service_update_user_status,
    delete_user
)

user_bp = Blueprint("user", __name__)


@user_bp.route("/", methods=["GET"])
@token_required
def get_users():
    return get_all_users()


@user_bp.route("/<int:user_id>", methods=["GET"])
@token_required
def get_user(user_id):

    if g.user["user_id"] != user_id and g.user["role"] != "ADMIN":
        return {
            "success": False,
            "message": "Access denied"
        }, 403

    return get_user_by_id(user_id)


@user_bp.route("/<int:user_id>", methods=["PUT"])
@token_required
def update_user_route(user_id):

    if g.user["user_id"] != user_id and g.user["role"] != "ADMIN":
        return {
            "success": False,
            "message": "Access denied"
        }, 403

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_user(user_id, data)


@user_bp.route("/<int:user_id>/status", methods=["PATCH"])
@token_required
@roles_required("ADMIN")
def update_user_status_route(user_id):

    data = request.get_json(silent=True)

    if not data or "account_status" not in data:
        return {
            "success": False,
            "message": "account_status is required"
        }, 400

    return service_update_user_status(
        user_id,
        data["account_status"]
    )


@user_bp.route("/<int:user_id>", methods=["DELETE"])
@token_required
@roles_required("ADMIN")
def delete_user_route(user_id):
    return delete_user(user_id)