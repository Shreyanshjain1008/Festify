from flask import Blueprint, g, jsonify, request
from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required
from app.services.day_pass_service import get_user_day_passes, register_day_pass

day_pass_bp = Blueprint("day_pass", __name__)

@day_pass_bp.route("/me", methods=["GET"])
@token_required
@roles_required("PARTICIPANT")
def my_day_passes():
    result, status = get_user_day_passes(g.user["user_id"])
    return jsonify(result), status

@day_pass_bp.route("/register", methods=["POST"])
@token_required
@roles_required("PARTICIPANT")
def create_day_pass():
    payload = request.get_json(silent=True) or {}
    result, status = register_day_pass(g.user["user_id"], payload.get("festival_day"))
    return jsonify(result), status
