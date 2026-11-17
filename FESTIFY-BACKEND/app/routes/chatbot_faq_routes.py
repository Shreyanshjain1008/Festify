from flask import Blueprint, request

from app.middleware.auth_middleware import token_required
from app.middleware.role_middleware import roles_required

from app.services.chatbot_faq_service import (
    get_all_faqs,
    search_faq,
    create_faq,
    update_faq,
    delete_faq
)


chatbot_faq_bp = Blueprint(
    "chatbot_faq",
    __name__
)


# =========================================================
# GET FAQS
# PUBLIC
# =========================================================

@chatbot_faq_bp.route("/", methods=["GET"])
def get_faqs_route():

    return get_all_faqs(
        category=request.args.get("category")
    )


# =========================================================
# ASK FAQ / CHATBOT
# PUBLIC
# =========================================================

@chatbot_faq_bp.route("/ask", methods=["POST"])
def ask_faq_route():

    data = request.get_json(silent=True)

    if not data or "question" not in data:
        return {
            "success": False,
            "message": "question is required"
        }, 400

    return search_faq(
        data["question"]
    )


# =========================================================
# CREATE FAQ
# ADMIN ONLY
# =========================================================

@chatbot_faq_bp.route("/", methods=["POST"])
@token_required
@roles_required("ADMIN")
def create_faq_route():

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return create_faq(data)


# =========================================================
# UPDATE FAQ
# ADMIN ONLY
# =========================================================

@chatbot_faq_bp.route(
    "/<int:faq_id>",
    methods=["PUT"]
)
@token_required
@roles_required("ADMIN")
def update_faq_route(faq_id):

    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required"
        }, 400

    return update_faq(
        faq_id,
        data
    )


# =========================================================
# DELETE FAQ
# ADMIN ONLY
# =========================================================

@chatbot_faq_bp.route(
    "/<int:faq_id>",
    methods=["DELETE"]
)
@token_required
@roles_required("ADMIN")
def delete_faq_route(faq_id):

    return delete_faq(
        faq_id
    )