
import smtplib
from email.message import EmailMessage

from app.config.config import Config


def send_otp_email(recipient, otp):
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        raise RuntimeError("Email credentials are not configured.")

    message = EmailMessage()
    message["Subject"] = "Your Festify Verification Code"
    message["From"] = (
        Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
    )
    message["To"] = recipient

    message.set_content(
        f"""Hello,

Your Festify email verification code is: {otp}

This code expires in {Config.OTP_EXPIRY_SECONDS // 60} minute(s).
Please do not share this code with anyone.

If you did not request this code, you can ignore this email.

Regards,
Festify Team
"""
    )

    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()

        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(message)


def send_event_pass_email(recipient, name, event_name, event_day, pass_token, qr_base64):
    """Email a day-specific QR pass after successful event registration."""
    import base64
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        raise RuntimeError("Email credentials are not configured.")
    from email.message import EmailMessage
    message = EmailMessage()
    message["Subject"] = f"Festify QR Pass — {event_name} ({event_day})"
    message["From"] = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
    message["To"] = recipient
    message.set_content(
        f"Hello {name},\n\nYour registration is confirmed.\n"
        f"Event: {event_name}\nFestival day: {event_day}\n"
        f"Pass token: {pass_token}\n\nPlease show the attached QR code at entry.\n\nFestify Team"
    )
    message.add_attachment(base64.b64decode(qr_base64), maintype="image", subtype="png", filename=f"festify-{event_day.lower()}.png")
    with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
        if Config.MAIL_USE_TLS:
            server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(message)
