from datetime import datetime

from app.extensions import db
from app.models.event import Event
from app.models.organizer_profile import OrganizerProfile
from app.models.venue import Venue
from app.models.event_custom_fields import EventCustomField
from app.models.fest_pass import DAY_TO_DATE

REQUIRED_EVENT_FIELDS = [
    "organizer_id", "event_name", "description", "category",
    "fest_day", "start_time", "end_time", "capacity",
    "registration_deadline"
]

VALID_FIELD_TYPES = ["TEXT", "NUMBER", "EMAIL", "DROPDOWN", "DATE", "URL"]


def _parse_event_datetime_fields(data):
    parsed = {}
    parsed["event_date"] = DAY_TO_DATE[data["fest_day"]]
    parsed["start_time"] = datetime.strptime(data["start_time"], "%H:%M").time()
    parsed["end_time"] = datetime.strptime(data["end_time"], "%H:%M").time()
    parsed["registration_deadline"] = datetime.strptime(
        data["registration_deadline"], "%Y-%m-%d %H:%M:%S"
    )
    return parsed


def check_venue_conflict(venue_id, event_date, start_time, end_time, exclude_event_id=None):
    if not venue_id:
        return None
    query = Event.query.filter(
        Event.venue_id == venue_id,
        Event.event_date == event_date,
        Event.status.in_(["APPROVED", "PUBLISHED"]),
        Event.start_time < end_time,
        Event.end_time > start_time
    )
    if exclude_event_id:
        query = query.filter(Event.event_id != exclude_event_id)
    return query.first()


def event_to_dict(event):
    return {
        "event_id": event.event_id,
        "organizer_id": event.organizer_id,
        "event_name": event.event_name,
        "description": event.description,
        "category": event.category,
        "fest_day": getattr(event, "fest_day", None) or "Day-1",
        "event_date": event.event_date.isoformat() if event.event_date else None,
        "start_time": event.start_time.strftime("%H:%M") if event.start_time else None,
        "end_time": event.end_time.strftime("%H:%M") if event.end_time else None,
        "venue_id": event.venue_id,
        "capacity": event.capacity,
        "eligibility": event.eligibility,
        "rules": event.rules,
        "registration_deadline": event.registration_deadline.isoformat() if event.registration_deadline else None,
        "event_image": event.event_image,
        "attendance_count": event.attendance_count,
        "status": event.status,
        "rejection_reason": event.rejection_reason,
        "date_created": event.date_created.isoformat() if event.date_created else None,
        "date_updated": event.date_updated.isoformat() if event.date_updated else None,
    }


def create_event(data):
    for field in REQUIRED_EVENT_FIELDS:
        if field not in data or data[field] in (None, ""):
            return {"success": False, "message": f"{field} is required"}, 400

    if data["fest_day"] not in DAY_TO_DATE:
        return {"success": False, "message": "fest_day must be Day-1, Day-2 or Day-3"}, 400

    organizer = OrganizerProfile.query.get(data["organizer_id"])
    if not organizer:
        return {"success": False, "message": "Organizer profile not found"}, 404
    if organizer.organizer_status != "APPROVED":
        return {"success": False, "message": "Organizer is not approved"}, 403

    if data.get("venue_id") and not Venue.query.get(data["venue_id"]):
        return {"success": False, "message": "Venue not found"}, 404

    try:
        parsed = _parse_event_datetime_fields(data)
    except ValueError:
        return {"success": False, "message": "Invalid date/time format"}, 400

    if parsed["end_time"] <= parsed["start_time"]:
        return {"success": False, "message": "end_time must be after start_time"}, 400
    if data.get("capacity", 0) <= 0:
        return {"success": False, "message": "capacity must be greater than 0"}, 400

    try:
        event = Event(
            organizer_id=data["organizer_id"], event_name=data["event_name"],
            description=data["description"], category=data["category"],
            fest_day=data["fest_day"],  
            event_date=parsed["event_date"], start_time=parsed["start_time"],
            end_time=parsed["end_time"], venue_id=data.get("venue_id"),
            capacity=data["capacity"], eligibility=data.get("eligibility"),
            rules=data.get("rules"), registration_deadline=parsed["registration_deadline"],
            event_image=data.get("event_image"), status="DRAFT"
        )
        db.session.add(event)
        db.session.commit()
        return {"success": True, "message": "Event created successfully", "event_id": event.event_id}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to create event", "error": str(e)}, 500



def _get_society_name(organizer):
    """Return the society/organization name using the available profile fields."""
    if not organizer:
        return None

    for field in ("society_name", "organization_name", "name"):
        value = getattr(organizer, field, None)
        if value:
            return value

    return None


def get_all_events(status_filter=None):
    """
    Return all events for management purposes.
    An optional status_filter can restrict the results.
    """
    query = Event.query

    if status_filter:
        query = query.filter(Event.status == status_filter)

    events = query.order_by(
        Event.event_date.asc(),
        Event.start_time.asc()
    ).all()

    return {
        "success": True,
        "events": [event_to_dict(event) for event in events]
    }, 200


def get_published_events(category=None, society=None, event_date=None):
    """
    Return only published events for the student-facing Explore Events page.

    Optional filters:
    - category: event category
    - society: organizer/society name
    - event_date: YYYY-MM-DD
    """
    query = Event.query.filter(Event.status == "PUBLISHED")

    if category:
        query = query.filter(Event.category.ilike(category.strip()))

    if event_date:
        try:
            parsed_date = datetime.strptime(
                event_date, "%Y-%m-%d"
            ).date()
        except ValueError:
            return {
                "success": False,
                "message": "event_date must use YYYY-MM-DD format"
            }, 400

        query = query.filter(Event.event_date == parsed_date)

    events = query.order_by(
        Event.event_date.asc(),
        Event.start_time.asc()
    ).all()

    results = []

    for event in events:
        item = event_to_dict(event)

        organizer = OrganizerProfile.query.get(event.organizer_id)
        society_name = _get_society_name(organizer)

        item["society_name"] = society_name

        if society and (
            not society_name
            or society_name.casefold() != society.strip().casefold()
        ):
            continue

        results.append(item)

    return {
        "success": True,
        "count": len(results),
        "events": results
    }, 200


def get_event_by_id(event_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    return {"success": True, "event": event_to_dict(event)}, 200


def update_event(event_id, organizer_id, data):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to edit this event"}, 403
    if event.status not in ("DRAFT", "REJECTED"):
        return {"success": False, "message": "Only DRAFT or REJECTED events can be edited"}, 400
    if "fest_day" in data and data["fest_day"] not in DAY_TO_DATE:
        return {"success": False, "message": "fest_day must be Day-1, Day-2 or Day-3"}, 400
    editable_fields = ["event_name", "description", "category", "fest_day", "capacity",
                        "eligibility", "rules", "event_image", "venue_id"]
    for field in editable_fields:
        if field in data:
            setattr(event, field, data[field])

    try:
        if any(k in data for k in ("fest_day", "start_time", "end_time", "registration_deadline")):
            merged = {
                "fest_day": event.fest_day,
                "start_time": data.get("start_time", event.start_time.strftime("%H:%M")),
                "end_time": data.get("end_time", event.end_time.strftime("%H:%M")),
                "registration_deadline": data.get(
                    "registration_deadline", event.registration_deadline.strftime("%Y-%m-%d %H:%M:%S")
                ),
            }
            parsed = _parse_event_datetime_fields(merged)
            event.event_date = parsed["event_date"]
            event.start_time = parsed["start_time"]
            event.end_time = parsed["end_time"]
            event.registration_deadline = parsed["registration_deadline"]

        db.session.commit()
        return {"success": True, "message": "Event updated successfully"}, 200
    except ValueError:
        db.session.rollback()
        return {"success": False, "message": "Invalid date/time format"}, 400
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to update event", "error": str(e)}, 500


def submit_event(event_id, organizer_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to submit this event"}, 403
    if event.status != "DRAFT":
        return {"success": False, "message": "Only DRAFT events can be submitted"}, 400

    conflict = check_venue_conflict(event.venue_id, event.event_date, event.start_time,
                                     event.end_time, exclude_event_id=event.event_id)
    if conflict:
        return {"success": False, "message": f"Venue conflict with event '{conflict.event_name}'"}, 409

    try:
        event.status = "PENDING"
        db.session.commit()
        return {"success": True, "message": "Event submitted for approval"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to submit event", "error": str(e)}, 500


def approve_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.status != "PENDING":
        return {"success": False, "message": "Only PENDING events can be approved"}, 400

    conflict = check_venue_conflict(event.venue_id, event.event_date, event.start_time,
                                     event.end_time, exclude_event_id=event.event_id)
    if conflict:
        return {"success": False, "message": f"Cannot approve: venue conflict with '{conflict.event_name}'"}, 409

    try:
        event.status = "APPROVED"
        event.rejection_reason = None
        db.session.commit()
        return {"success": True, "message": "Event approved successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to approve event", "error": str(e)}, 500


def reject_event(event_id, reason):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.status != "PENDING":
        return {"success": False, "message": "Only PENDING events can be rejected"}, 400
    if not reason:
        return {"success": False, "message": "Rejection reason is required"}, 400

    try:
        event.status = "REJECTED"
        event.rejection_reason = reason
        db.session.commit()
        return {"success": True, "message": "Event rejected"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to reject event", "error": str(e)}, 500


def publish_event(event_id, organizer_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to publish this event"}, 403
    if event.status != "APPROVED":
        return {"success": False, "message": "Only APPROVED events can be published"}, 400

    try:
        event.status = "PUBLISHED"
        db.session.commit()
        return {"success": True, "message": "Event published successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to publish event", "error": str(e)}, 500


def cancel_event(event_id, organizer_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to cancel this event"}, 403
    if event.status in ("COMPLETED", "CANCELLED"):
        return {"success": False, "message": f"Event is already {event.status}"}, 400

    try:
        event.status = "CANCELLED"
        db.session.commit()
        return {"success": True, "message": "Event cancelled successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to cancel event", "error": str(e)}, 500


def complete_event(event_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.status != "PUBLISHED":
        return {"success": False, "message": "Only PUBLISHED events can be marked as completed"}, 400

    try:
        event.status = "COMPLETED"
        db.session.commit()
        return {"success": True, "message": "Event marked as completed"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to complete event", "error": str(e)}, 500


def delete_event(event_id, organizer_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to delete this event"}, 403
    if event.status != "DRAFT":
        return {"success": False, "message": "Only DRAFT events can be deleted"}, 400

    try:
        db.session.delete(event)
        db.session.commit()
        return {"success": True, "message": "Event deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to delete event", "error": str(e)}, 500


def increment_attendance(event_id):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404

    try:
        db.session.query(Event).filter(Event.event_id == event_id).update(
            {Event.attendance_count: Event.attendance_count + 1}
        )
        db.session.commit()
        db.session.refresh(event)
        return {"success": True, "message": "Attendance recorded", "attendance_count": event.attendance_count}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to record attendance", "error": str(e)}, 500


def add_custom_field(event_id, organizer_id, data):
    event = Event.query.get(event_id)
    if not event:
        return {"success": False, "message": "Event not found"}, 404
    if event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to modify this event"}, 403
    if event.status not in ("DRAFT", "REJECTED"):
        return {"success": False, "message": "Custom fields can only be added while the event is in DRAFT"}, 400

    field_name = data.get("field_name")
    field_type = data.get("field_type")
    if not field_name:
        return {"success": False, "message": "field_name is required"}, 400
    if field_type not in VALID_FIELD_TYPES:
        return {"success": False, "message": f"field_type must be one of: {', '.join(VALID_FIELD_TYPES)}"}, 400
    if field_type == "DROPDOWN" and not data.get("field_options"):
        return {"success": False, "message": "field_options is required for DROPDOWN fields"}, 400

    try:
        field = EventCustomField(
            event_id=event_id, field_name=field_name, field_type=field_type,
            is_required=data.get("is_required", False), field_options=data.get("field_options"),
            display_order=data.get("display_order")
        )
        db.session.add(field)
        db.session.commit()
        return {"success": True, "message": "Custom field added successfully", "custom_field_id": field.custom_field_id}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to add custom field", "error": str(e)}, 500


def update_custom_field(custom_field_id, organizer_id, data):
    field = EventCustomField.query.get(custom_field_id)
    if not field:
        return {"success": False, "message": "Custom field not found"}, 404
    if field.event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to modify this field"}, 403
    if "field_type" in data and data["field_type"] not in VALID_FIELD_TYPES:
        return {"success": False, "message": f"field_type must be one of: {', '.join(VALID_FIELD_TYPES)}"}, 400

    for f in ["field_name", "field_type", "is_required", "field_options", "display_order"]:
        if f in data:
            setattr(field, f, data[f])

    try:
        db.session.commit()
        return {"success": True, "message": "Custom field updated successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to update custom field", "error": str(e)}, 500


def delete_custom_field(custom_field_id, organizer_id):
    field = EventCustomField.query.get(custom_field_id)
    if not field:
        return {"success": False, "message": "Custom field not found"}, 404
    if field.event.organizer_id != organizer_id:
        return {"success": False, "message": "You do not have permission to delete this field"}, 403

    try:
        db.session.delete(field)
        db.session.commit()
        return {"success": True, "message": "Custom field deleted successfully"}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to delete custom field", "error": str(e)}, 500


def get_custom_fields_for_event(event_id):
    fields = EventCustomField.query.filter_by(event_id=event_id).order_by(EventCustomField.display_order).all()
    return {"success": True, "fields": [
        {"custom_field_id": f.custom_field_id, "event_id": f.event_id, "field_name": f.field_name,
         "field_type": f.field_type, "is_required": f.is_required,
         "field_options": f.field_options, "display_order": f.display_order}
        for f in fields
    ]}, 200