
from datetime import datetime, date as date_cls
import requests

from flask import current_app
from app.extensions import db
from app.models.fest_pass import FestPass, DAY_TO_DATE
from app.models.user import User
from app.config.config import Config
from app.utils.qr_generator import (
    generate_pass_token,
    generate_qr_code_base64,
    pass_verify_url
)


DATE_TO_DAY = {v: k for k, v in DAY_TO_DATE.items()}

BREVO_EMAIL_API_URL = "https://api.brevo.com/v3/smtp/email"


def serialize_day_pass(row, include_qr=True):
    data = {
        "fest_pass_id": row.fest_pass_id,
        "festival_day": row.festival_day or DATE_TO_DAY.get(row.fest_date),
        "fest_date": row.fest_date.isoformat() if row.fest_date else None,
        "status": row.pass_status,
        "pass_status": row.pass_status,
        "issued_at": row.issued_at.isoformat() if row.issued_at else None,
        "created_at": row.issued_at.isoformat() if row.issued_at else None,
        "pass_token": row.pass_token
    }

    if include_qr:
        data["qr_code_base64"] = generate_qr_code_base64(
            pass_verify_url(row.pass_token)
        )

    return data


def _email_day_pass(user, row, qr_b64):
    if not Config.BREVO_API_KEY or not Config.BREVO_SENDER_EMAIL:
        raise RuntimeError("Brevo email credentials are not configured.")

    day = row.festival_day or DATE_TO_DAY.get(row.fest_date, "Festival day")

    payload = {
        "sender": {
            "name": Config.BREVO_SENDER_NAME or "Festify",
            "email": Config.BREVO_SENDER_EMAIL
        },
        "to": [{"email": user.email}],
        "subject": f"Festify Campus QR Pass — {day}",
        "textContent": (
            f"Hello {getattr(user, 'name', 'Student')},\n\n"
            f"Your campus entry pass for {day} ({row.fest_date}) is confirmed. "
            "This is separate from event registration.\n"
            f"Pass token: {row.pass_token}\n\n"
            "Show the attached QR code at campus entry.\n\nFestify Team"
        ),
        "attachment": [
            {
                "content": qr_b64,
                "name": f"festify-campus-{day.lower()}.png"
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


def get_user_day_passes(user_id):
    rows = FestPass.query.filter_by(user_id=user_id).order_by(
        FestPass.fest_date.asc()
    ).all()

    return {
        "success": True,
        "day_passes": [serialize_day_pass(row) for row in rows]
    }, 200


def register_day_pass(user_id, festival_day):
    festival_day = str(festival_day or "").strip()

    if festival_day not in DAY_TO_DATE:
        return {
            "success": False,
            "message": "Choose Day-1, Day-2, or Day-3."
        }, 400

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "Student account not found."
        }, 404

    fest_date = DAY_TO_DATE[festival_day]

    existing = FestPass.query.filter_by(
        user_id=user_id,
        fest_date=fest_date
    ).first()

    if existing and existing.pass_status == "ACTIVE":
        qr = generate_qr_code_base64(
            pass_verify_url(existing.pass_token)
        )

        return {
            "success": True,
            "message": f"Your {festival_day} campus QR pass has already been issued. Please check your registered email.",
            "day_pass": serialize_day_pass(existing),
            "email_sent": True
        }, 200

    try:
        if existing:
            existing.pass_status = "ACTIVE"
            existing.pass_token = generate_pass_token()
            existing.issued_at = datetime.utcnow()
            existing.festival_day = festival_day
            row = existing

        else:
            row = FestPass(
                user_id=user_id,
                fest_date=fest_date,
                festival_day=festival_day,
                pass_token=generate_pass_token(),
                pass_status="ACTIVE",
                issued_at=datetime.utcnow()
            )

            db.session.add(row)

        db.session.flush()

        qr = generate_qr_code_base64(
            pass_verify_url(row.pass_token)
        )

        db.session.commit()

    except Exception as exc:
        db.session.rollback()

        return {
            "success": False,
            "message": f"Could not create campus pass: {exc}"
        }, 500

    try:
        _email_day_pass(user, row, qr)
        email_sent = True

    except Exception as exc:
        current_app.logger.warning(
            "Campus pass email failed for user %s (%s): %s",
            user_id,
            festival_day,
            exc
        )
        email_sent = False

    data = serialize_day_pass(row)
    data["email_sent"] = email_sent

    message = (
        f"Your {festival_day} campus QR pass has been sent to your registered email."
        if email_sent
        else f"Your {festival_day} pass is saved, but email delivery failed. Please check your Brevo email configuration."
    )

    return {
        "success": True,
        "message": message,
        "day_pass": data
    }, 201



# from datetime import datetime, date as date_cls
# from email.message import EmailMessage
# import base64
# import smtplib
# from flask import current_app
# from app.extensions import db
# from app.models.fest_pass import FestPass, DAY_TO_DATE
# from app.models.user import User
# from app.config.config import Config
# from app.utils.qr_generator import generate_pass_token, generate_qr_code_base64, pass_verify_url

# DATE_TO_DAY = {v: k for k, v in DAY_TO_DATE.items()}

# def serialize_day_pass(row, include_qr=True):
#     data = {"fest_pass_id": row.fest_pass_id, "festival_day": row.festival_day or DATE_TO_DAY.get(row.fest_date), "fest_date": row.fest_date.isoformat() if row.fest_date else None, "status": row.pass_status, "pass_status": row.pass_status, "issued_at": row.issued_at.isoformat() if row.issued_at else None, "created_at": row.issued_at.isoformat() if row.issued_at else None, "pass_token": row.pass_token}
#     if include_qr:
#         data["qr_code_base64"] = generate_qr_code_base64(pass_verify_url(row.pass_token))
#     return data

# def _email_day_pass(user, row, qr_b64):
#     if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
#         raise RuntimeError("Email credentials are not configured.")
#     day = row.festival_day or DATE_TO_DAY.get(row.fest_date, "Festival day")
#     msg = EmailMessage()
#     msg["Subject"] = f"Festify Campus QR Pass — {day}"
#     msg["From"] = Config.MAIL_DEFAULT_SENDER or Config.MAIL_USERNAME
#     msg["To"] = user.email
#     msg.set_content(f"Hello {getattr(user, 'name', 'Student')},\n\nYour campus entry pass for {day} ({row.fest_date}) is confirmed. This is separate from event registration.\nPass token: {row.pass_token}\n\nShow the attached QR code at campus entry.\n\nFestify Team")
#     msg.add_attachment(base64.b64decode(qr_b64), maintype="image", subtype="png", filename=f"festify-campus-{day.lower()}.png")
#     with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
#         if Config.MAIL_USE_TLS: server.starttls()
#         server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
#         server.send_message(msg)

# def get_user_day_passes(user_id):
#     rows = FestPass.query.filter_by(user_id=user_id).order_by(FestPass.fest_date.asc()).all()
#     return {"success": True, "day_passes": [serialize_day_pass(row) for row in rows]}, 200

# def register_day_pass(user_id, festival_day):
#     festival_day = str(festival_day or "").strip()
#     if festival_day not in DAY_TO_DATE:
#         return {"success": False, "message": "Choose Day-1, Day-2, or Day-3."}, 400
#     user = User.query.get(user_id)
#     if not user:
#         return {"success": False, "message": "Student account not found."}, 404
#     fest_date = DAY_TO_DATE[festival_day]
#     existing = FestPass.query.filter_by(user_id=user_id, fest_date=fest_date).first()
#     if existing and existing.pass_status == "ACTIVE":
#         qr = generate_qr_code_base64(pass_verify_url(row.pass_token))
#         return {"success": True, "message": f"Your {festival_day} campus QR pass has already been issued. Please check your registered email.", "day_pass": serialize_day_pass(existing), "email_sent": True}, 200
#     try:
#         if existing:
#             existing.pass_status = "ACTIVE"
#             existing.pass_token = generate_pass_token()
#             existing.issued_at = datetime.utcnow()
#             existing.festival_day = festival_day
#             row = existing
#         else:
#             row = FestPass(user_id=user_id, fest_date=fest_date, festival_day=festival_day, pass_token=generate_pass_token(), pass_status="ACTIVE", issued_at=datetime.utcnow())
#             db.session.add(row)
#         db.session.flush()
#         qr = generate_qr_code_base64(pass_verify_url(row.pass_token))
#         db.session.commit()
#     except Exception as exc:
#         db.session.rollback()
#         return {"success": False, "message": f"Could not create campus pass: {exc}"}, 500
#     try:
#         _email_day_pass(user, row, qr)
#         email_sent = True
#     except Exception as exc:
#         current_app.logger.warning("Campus pass email failed for user %s (%s): %s", user_id, festival_day, exc)
#         email_sent = False
#     data = serialize_day_pass(row)
#     data["email_sent"] = email_sent
#     message = f"Your {festival_day} campus QR pass has been sent to your registered email." if email_sent else f"Your {festival_day} pass is saved, but email delivery failed. Please check SMTP settings."
#     return {"success": True, "message": message, "day_pass": data}, 201
