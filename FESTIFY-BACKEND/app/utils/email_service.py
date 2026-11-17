
import base64
import requests

from app.config.config import Config


BREVO_EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"


def send_otp_email(recipient, otp):
    if not Config.BREVO_API_KEY or not Config.BREVO_SENDER_EMAIL:
        raise RuntimeError("Brevo email credentials are not configured.")

    payload = {
        "sender": {
            "name": Config.BREVO_SENDER_NAME or "Festify",
            "email": Config.BREVO_SENDER_EMAIL
        },
        "to": [{"email": recipient}],
        "subject": "Your Festify Verification Code",
        "textContent": (
            f"""Hello,

Your Festify email verification code is: {otp}

This code expires in {Config.OTP_EXPIRY_SECONDS // 60} minute(s).
Please do not share this code with anyone.

If you did not request this code, you can ignore this email.

Regards,
Festify Team
"""
        )
    }

    response = requests.post(
        BREVO_EMAIL_API_URL,
        json=payload,
        headers={
            "api-key": Config.BREVO_API_KEY,
            "accept": "application/json",
            "content-type": "application/json"
        },
        timeout=20
    )

    response.raise_for_status()


def send_event_pass_email(recipient, name, event_name, event_day, pass_token, qr_base64):
    """Email a day-specific QR pass after successful event registration."""

    if not Config.BREVO_API_KEY or not Config.BREVO_SENDER_EMAIL:
        raise RuntimeError("Brevo email credentials are not configured.")

    payload = {
        "sender": {
            "name": Config.BREVO_SENDER_NAME or "Festify",
            "email": Config.BREVO_SENDER_EMAIL
        },
        "to": [{"email": recipient}],
        "subject": f"Festify QR Pass - {event_name} ({event_day})",
        "textContent": (
            f"Hello {name},\n\nYour registration is confirmed.\n"
            f"Event: {event_name}\nFestival day: {event_day}\n"
            f"Pass token: {pass_token}\n\n"
            "Please show the attached QR code at entry.\n\nFestify Team"
        ),
        "attachment": [
            {
                "content": qr_base64,
                "name": f"festify-{event_day.lower()}.png"
            }
        ]
    }

    response = requests.post(
        BREVO_EMAIL_API_URL,
        json=payload,
        headers={
            "api-key": Config.BREVO_API_KEY,
            "accept": "application/json",
            "content-type": "application/json"
        },
        timeout=20
    )

    response.raise_for_status()

