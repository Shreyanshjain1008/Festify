
from flask import Blueprint, request

from app.services.auth_service import register_user, login_user
from app.utils.email_service import send_otp_email
from app.utils.otp import (
    generate_otp,
    store_otp,
    verify_otp,
    is_email_verified,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/send-email-otp", methods=["POST"])
def send_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    if not email or "@" not in email:
        return {
            "success": False,
            "message": "Please provide a valid email address.",
        }, 400

    try:
        otp = generate_otp()

        # Send first so a failed email delivery does not create
        # a new usable OTP in the store.
        send_otp_email(email, otp)
        store_otp(email, otp)

        return {
            "success": True,
            "message": "OTP sent successfully. Please check your email.",
        }, 200

    except Exception as e:
        import traceback

        traceback.print_exc()

        return {
            "success": False,
            "message": f"Email error: {str(e)}",
        }, 500


@auth_bp.route("/verify-email-otp", methods=["POST"])
def verify_email_otp():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    otp = str(data.get("otp", "")).strip()

    if not email or not otp:
        return {
            "success": False,
            "message": "Email and OTP are required.",
        }, 400

    if not otp.isdigit() or len(otp) != 6:
        return {
            "success": False,
            "message": "Enter a valid six-digit OTP.",
        }, 400

    try:
        success, message = verify_otp(email, otp)

        if not success:
            return {
                "success": False,
                "message": message,
            }, 400

        return {
            "success": True,
            "message": "Email verified successfully!",
        }, 200

    except Exception:
        import logging
        logging.exception("Failed to verify Festify email OTP")

        return {
            "success": False,
            "message": "OTP verification failed due to a server error.",
        }, 500


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required.",
        }, 400

    email = str(data.get("email", "")).strip().lower()

    if not is_email_verified(email):
        return {
            "success": False,
            "message": "Please verify your email before registering.",
        }, 400

    # Keep your existing registration service and its field validation.
    return register_user(data)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)

    if not data:
        return {
            "success": False,
            "message": "Request body is required.",
        }, 400

    return login_user(data.get("email"), data.get("password"))

