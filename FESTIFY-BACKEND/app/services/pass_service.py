from datetime import datetime, date as date_cls

from app.extensions import db
from app.models.fest_pass import FestPass
from app.models.user import User
from app.utils.qr_generator import generate_pass_token, generate_qr_code_base64
from html import escape


def pass_to_dict(fest_pass):
    return {
        "fest_pass_id": fest_pass.fest_pass_id,
        "user_id": fest_pass.user_id,
        "fest_date": fest_pass.fest_date.isoformat() if fest_pass.fest_date else None,
        "pass_token": fest_pass.pass_token,
        "pass_status": fest_pass.pass_status,
        "issued_at": fest_pass.issued_at.isoformat() if fest_pass.issued_at else None,
    }


def issue_pass(user_id, fest_date_str):
    if not User.query.get(user_id):
        return {"success": False, "message": "User not found"}, 404

    try:
        fest_date = datetime.strptime(fest_date_str, "%Y-%m-%d").date()
    except ValueError:
        return {"success": False, "message": "fest_date must be in YYYY-MM-DD format"}, 400

    if FestPass.query.filter_by(user_id=user_id, fest_date=fest_date).first():
        return {"success": False, "message": "Pass already issued for this date"}, 409

    try:
        token = generate_pass_token()
        fest_pass = FestPass(user_id=user_id, fest_date=fest_date, pass_token=token, pass_status="ACTIVE")
        db.session.add(fest_pass)
        db.session.commit()
        return {
            "success": True, "message": "Pass issued successfully",
            "pass": pass_to_dict(fest_pass), "qr_code_base64": generate_qr_code_base64(token)
        }, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to issue pass", "error": str(e)}, 500


def get_pass_by_id(fest_pass_id):
    fest_pass = FestPass.query.get(fest_pass_id)
    if not fest_pass:
        return {"success": False, "message": "Pass not found"}, 404
    return {"success": True, "pass": pass_to_dict(fest_pass)}, 200


def validate_pass_by_id(fest_pass_id):
    fest_pass = FestPass.query.get(fest_pass_id)
    if not fest_pass:
        return {"success": False, "message": "Pass not found"}, 404

    if fest_pass.pass_status == "USED":
        return {"success": False, "message": "This pass has already been used"}, 400
    if fest_pass.pass_status == "CANCELLED":
        return {"success": False, "message": "This pass has been cancelled"}, 400
    if fest_pass.pass_status == "EXPIRED" or fest_pass.fest_date < date_cls.today():
        fest_pass.pass_status = "EXPIRED"
        db.session.commit()
        return {"success": False, "message": "This pass has expired"}, 400

    try:
        fest_pass.pass_status = "USED"
        db.session.commit()
        return {"success": True, "message": "Pass validated successfully. Entry granted."}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to validate pass", "error": str(e)}, 500


def cancel_pass(fest_pass_id, user_id):
    fest_pass = FestPass.query.get(fest_pass_id)
    if not fest_pass:
        return {"success": False, "message": "Pass not found"}, 404
    if fest_pass.user_id != user_id:
        return {"success": False, "message": "You do not have permission to cancel this pass"}, 403
    if fest_pass.pass_status != "ACTIVE":
        return {"success": False, "message": f"Cannot cancel a pass that is {fest_pass.pass_status}"}, 400

    try:
        fest_pass.pass_status = "CANCELLED"
        db.session.commit()
        return {"success": True, "message": "Pass cancelled successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to cancel pass", "error": str(e)}, 500


def get_user_passes(user_id):
    passes = FestPass.query.filter_by(user_id=user_id).all()
    return {"success": True, "passes": [pass_to_dict(p) for p in passes]}, 200


def _info_rows(pairs):
    return "".join(
        f"<p><span>{label}</span><b>{escape(str(value))}</b></p>"
        for label, value in pairs
    )


def render_pass_page(token):
    fp = FestPass.query.filter_by(pass_token=token).first()
    user = User.query.get(fp.user_id) if fp else None

    if not fp or not user:
        label, color, body = "INVALID PASS", "#c62828", ""
    else:
        if fp.pass_status == "USED":
            label, color = "ALREADY USED", "#ef6c00"
        elif fp.pass_status == "CANCELLED":
            label, color = "CANCELLED", "#c62828"
        elif fp.pass_status == "EXPIRED" or fp.fest_date < date_cls.today():
            label, color = "EXPIRED", "#c62828"
        else:
            label, color = "VALID PASS", "#2e7d32"

        dob = user.date_of_birth.strftime("%d %b %Y") if user.date_of_birth else "-"
        student_rows = _info_rows([
            ("Enrollment", user.college_id_number),
            ("College", user.college_name),
            ("Branch", user.branch),
            ("Year of study", user.year_of_study),
            ("Email", user.email),
            ("Phone", user.phone),
            ("Date of birth", dob),
            ("Gender", user.gender),
        ])
        pass_rows = _info_rows([
            ("Pass ID", fp.fest_pass_id),
            ("Festival day", fp.day_label),
            ("Date", fp.fest_date.strftime("%d %b %Y")),
        ])
        body = (
            '<div class="who">'
            f'<div class="av">{escape(user.name[:1].upper())}</div>'
            f"<h2>{escape(user.name)}</h2>"
            "</div>"
            f"<h3>Student details</h3>{student_rows}"
            f"<h3>Pass details</h3>{pass_rows}"
        )

    return (
        '<!doctype html><html><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        "<title>Festify Pass</title>"
        "<style>"
        "body{font-family:sans-serif;margin:0;background:#111;color:#fff}"
        f".b{{background:{color};padding:26px;text-align:center;"
        "font-size:26px;font-weight:700}"
        ".c{padding:20px}"
        ".who{text-align:center;padding:8px 0 4px}"
        ".av{width:72px;height:72px;margin:0 auto 10px;border-radius:50%;"
        "background:#6c5ce7;font-size:32px;font-weight:700;"
        "display:flex;align-items:center;justify-content:center}"
        ".who h2{margin:0 0 8px;font-size:24px}"
        "h3{margin:22px 0 4px;font-size:13px;letter-spacing:1px;"
        "text-transform:uppercase;color:#8b7cf6}"
        "p{display:flex;justify-content:space-between;gap:16px;"
        "border-bottom:1px solid #333;padding:12px 0;margin:0}"
        "p b{text-align:right;word-break:break-word}"
        "span{color:#aaa}"
        "</style></head><body>"
        f'<div class="b">{label}</div><div class="c">{body}</div>'
        "</body></html>"
    )