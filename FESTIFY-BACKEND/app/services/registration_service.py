from datetime import datetime
from app.extensions import db
from app.models.event import Event
from app.models.event_registration import EventRegistration
from app.models.event_custom_fields import EventCustomField
from app.models.event_registration_custom_value import EventRegistrationCustomValue
from app.models.user import User
from app.utils.validators import validate_custom_field_value

VALID_DAYS = {"Day-1", "Day-2", "Day-3"}


def registration_to_dict(registration, include_custom_values=False, include_qr=False):
    event = registration.event
    result = {
        "registration_id": registration.registration_id,
        "event_id": registration.event_id,
        "user_id": registration.user_id,
        "event_day": registration.event_day,
        "registration_status": registration.registration_status,
        "registration_date": registration.registration_date.isoformat() if registration.registration_date else None,
        "event": {
            "event_id": event.event_id,
            "event_name": event.event_name,
            "description": event.description,
            "category": event.category,
            "fest_day": event.fest_day,
            "event_date": event.event_date.isoformat() if event.event_date else None,
            "start_time": event.start_time.isoformat() if event.start_time else None,
            "end_time": event.end_time.isoformat() if event.end_time else None,
            "registration_deadline": event.registration_deadline.isoformat() if event.registration_deadline else None,
            "eligibility": event.eligibility,
            "rules": event.rules,
            "event_image": event.event_image,
            "status": event.status,
        } if event else None,
    }
    if include_custom_values:
        result["custom_values"] = [
            {"custom_field_id": cv.custom_field_id, "field_value": cv.field_value}
            for cv in registration.custom_values
        ]
    # Event registrations never create or return campus QR passes.
    return result


def _normalize_day(value):
    value = str(value or "Day-1").strip().replace(" ", "-")
    if value.lower() in {"day1", "day-1"}: return "Day-1"
    if value.lower() in {"day2", "day-2"}: return "Day-2"
    if value.lower() in {"day3", "day-3"}: return "Day-3"
    return value


def register_for_event(event_id, user_id, custom_field_values=None, event_day=None):
    event = Event.query.get(event_id)
    if not event:
        return False, "Event not found", None
    if event.status != "PUBLISHED":
        return False, "Event is not open for registration", None
    if event.registration_deadline and datetime.utcnow() > event.registration_deadline:
        return False, "Registration deadline has passed", None
    user = User.query.get(user_id)
    if not user:
        return False, "User not found", None

    # Registration day comes from the event itself, not from the student's campus pass selection.
    event_day = _normalize_day(getattr(event, "fest_day", None) or event_day or "Day-1")
    if event_day not in VALID_DAYS:
        return False, "This event has an invalid festival day. Please contact the organizer.", None

    existing = EventRegistration.query.filter_by(event_id=event_id, user_id=user_id, event_day=event_day).first()
    if existing and existing.registration_status != "CANCELLED":
        return False, f"Already registered for {event.event_name} on {event_day}", existing

    current_count = EventRegistration.query.filter_by(event_id=event_id, registration_status="CONFIRMED").count()
    if event.capacity is not None and current_count >= event.capacity:
        return False, "Event has reached full capacity", None

    custom_fields = EventCustomField.query.filter_by(event_id=event_id).all()
    custom_field_values = custom_field_values or {}
    for field in custom_fields:
        value = custom_field_values.get(str(field.custom_field_id))
        if field.is_required and (value is None or str(value).strip() == ""):
            return False, f"'{field.field_name}' is a required field", None
        if value is not None and str(value).strip() != "":
            valid, error = validate_custom_field_value(field.field_type, value, field.field_options)
            if not valid:
                return False, f"'{field.field_name}' {error}", None

    try:
        if existing:
            existing.registration_status = "CONFIRMED"
            existing.registration_date = datetime.utcnow()
            registration = existing
        else:
            registration = EventRegistration(
                event_id=event_id,
                user_id=user_id,
                event_day=event_day,
                registration_status="CONFIRMED",
            )
            db.session.add(registration)
        db.session.flush()
        for field_id, value in custom_field_values.items():
            db.session.add(EventRegistrationCustomValue(
                registration_id=registration.registration_id,
                custom_field_id=int(field_id),
                field_value=str(value),
            ))
        db.session.commit()
        return True, f"Successfully registered for {event.event_name} on {event_day}.", registration
    except Exception as exc:
        db.session.rollback()
        return False, f"Registration failed: {exc}", None


def cancel_registration(registration_id, user_id):
    registration = EventRegistration.query.get(registration_id)
    if not registration:
        return {"success": False, "message": "Registration not found"}, 404
    if registration.user_id != user_id:
        return {"success": False, "message": "You do not have permission to cancel this registration"}, 403
    registration.registration_status = "CANCELLED"
    db.session.commit()
    return {"success": True, "message": "Registration cancelled successfully"}, 200


def get_registrations_for_event(event_id):
    rows = EventRegistration.query.filter_by(event_id=event_id).all()
    return {"success": True, "registrations": [registration_to_dict(r) for r in rows]}, 200


def get_registrations_for_user(user_id):
    rows = EventRegistration.query.filter_by(user_id=user_id, registration_status="CONFIRMED").order_by(EventRegistration.registration_date.desc()).all()
    return {"success": True, "registrations": [registration_to_dict(r, include_qr=False) for r in rows]}, 200
