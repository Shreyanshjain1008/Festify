
import os
import smtplib
from email.message import EmailMessage
from app.config.config import Config
from flask import Blueprint, request, jsonify, current_app

from app.services.auth_service import register_user, login_user
from app.utils.otp import (
    generate_otp,
    store_otp,
    verify_otp,
    is_email_verified,
)

auth_bp = Blueprint("auth", __name__)





def send_otp_email(email, otp):
    """Send a six-digit verification OTP using Flask's mail configuration."""

    config = current_app.config

    smtp_host = config.get("MAIL_SERVER")
    smtp_port = config.get("MAIL_PORT", 587)
    smtp_username = config.get("MAIL_USERNAME")
    smtp_password = config.get("MAIL_PASSWORD")
    sender_email = config.get("MAIL_DEFAULT_SENDER") or smtp_username

    # Validate configuration before connecting to the mail server.
    if not all([
        smtp_host,
        smtp_port,
        smtp_username,
        smtp_password,
        sender_email,
    ]):
        raise RuntimeError(
            "Email configuration is incomplete. Check MAIL_SERVER, "
            "MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, and "
            "MAIL_DEFAULT_SENDER in your backend .env file."
        )

    message = EmailMessage()
    message["Subject"] = "Your Festify Email Verification OTP"
    message["From"] = sender_email
    message["To"] = email

    message.set_content(
        f"""Hello,

Your Festify email verification OTP is: {otp}

This code expires in 5 minutes. Do not share it with anyone.

If you did not request this code, you can ignore this email.

Thanks,
Festify Team
"""
    )

    if int(smtp_port) == 465:
        # SSL connection, commonly used on port 465.
        with smtplib.SMTP_SSL(
            smtp_host, int(smtp_port), timeout=20
        ) as server:
            server.login(smtp_username, smtp_password)
            server.send_message(message)
    else:
        # STARTTLS connection, commonly used on port 587.
        with smtplib.SMTP(
            smtp_host, int(smtp_port), timeout=20
        ) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(smtp_username, smtp_password)
            server.send_message(message)

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
