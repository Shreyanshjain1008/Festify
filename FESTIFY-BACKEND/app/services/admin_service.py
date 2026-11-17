from secrets import token_hex
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.models.society import Society
from app.models.organizer_profile import OrganizerProfile
from app.models.event import Event
from app.models.venue import Venue


# =========================================================
# USER MANAGEMENT
# =========================================================

def get_all_users_for_admin():

    try:
        users = User.query.all()

        return {
            "success": True,
            "users": [
                {
                    "user_id": user.user_id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "college_id_number": user.college_id_number,
                    "college_name": user.college_name,
                    "branch": user.branch,
                    "year_of_study": user.year_of_study,
                    "gender": user.gender,
                    "role": user.role,
                    "account_status": user.account_status,
                    "date_created": (
                        user.date_created.isoformat()
                        if user.date_created else None
                    )
                }
                for user in users
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch users",
            "error": str(e)
        }, 500


def update_user_status_by_admin(user_id, account_status):

    valid_statuses = [
        "ACTIVE",
        "INACTIVE",
        "BLOCKED"
    ]

    if account_status not in valid_statuses:
        return {
            "success": False,
            "message": "Invalid account status"
        }, 400

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, 404

    try:

        user.account_status = account_status

        db.session.commit()

        return {
            "success": True,
            "message": "User account status updated successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update user status",
            "error": str(e)
        }, 500


def delete_user_by_admin(user_id):

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, 404

    try:

        db.session.delete(user)
        db.session.commit()

        return {
            "success": True,
            "message": "User deleted successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to delete user",
            "error": str(e)
        }, 500


# =========================================================
# SOCIETY MANAGEMENT
# =========================================================

def get_all_societies_for_admin():

    try:

        societies = Society.query.all()

        return {
            "success": True,
            "societies": [
                {
                    "society_id": society.society_id,
                    "society_name": society.society_name,
                    "description": society.description,
                    "contact_email": society.contact_email,
                    "contact_phone": society.contact_phone,
                    "society_code": society.society_code,
                    "status": society.status,
                    "rejection_reason": society.rejection_reason,
                    "date_created": (
                        society.date_created.isoformat()
                        if society.date_created else None
                    )
                }
                for society in societies
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch societies",
            "error": str(e)
        }, 500


def create_approved_society(data):
    """Create an admin-managed society using its member contact details."""
    required = ("society_name", "contact_email", "contact_phone", "society_code")
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        return {"success": False, "message": f"Required fields: {', '.join(missing)}"}, 400

    society_name = str(data["society_name"]).strip()
    contact_email = str(data["contact_email"]).strip().lower()
    contact_phone = str(data["contact_phone"]).strip()
    society_code = str(data["society_code"]).strip().upper()
    description = str(data.get("description") or "").strip() or None

    if len(society_name) > 150 or len(contact_email) > 150 or len(contact_phone) > 15 or len(society_code) > 30:
        return {"success": False, "message": "One or more fields exceed the allowed length."}, 400
    if Society.query.filter_by(society_code=society_code).first():
        return {"success": False, "message": "This society code is already in use. Enter a unique code."}, 409

    try:
        society = Society(
            society_name=society_name,
            description=description,
            contact_email=contact_email,
            contact_phone=contact_phone,
            society_code=society_code,
            status="APPROVED",
            rejection_reason=None,
        )
        db.session.add(society)
        db.session.commit()
        return {"success": True, "message": "Society created and approved", "society": _society_admin_dict(society)}, 201
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to create society", "error": str(e)}, 500


def _society_admin_dict(society):
    return {
        "society_id": society.society_id,
        "society_name": society.society_name,
        "description": society.description,
        "contact_email": society.contact_email,
        "contact_phone": society.contact_phone,
        "society_code": society.society_code,
        "status": society.status,
        "rejection_reason": society.rejection_reason,
        "date_created": society.date_created.isoformat() if society.date_created else None,
    }


def update_society_by_admin(society_id, data):
    """Edit society details; contact details belong to a society member, not an organizer."""
    society = Society.query.get(society_id)
    if not society:
        return {"success": False, "message": "Society not found"}, 404

    required = ("society_name", "contact_email", "contact_phone", "society_code")
    missing = [field for field in required if not str(data.get(field, "")).strip()]
    if missing:
        return {"success": False, "message": f"Required fields: {', '.join(missing)}"}, 400

    society_name = str(data["society_name"]).strip()
    contact_email = str(data["contact_email"]).strip().lower()
    contact_phone = str(data["contact_phone"]).strip()
    society_code = str(data["society_code"]).strip().upper()
    description = str(data.get("description") or "").strip() or None

    if len(society_name) > 150 or len(contact_email) > 150 or len(contact_phone) > 15 or len(society_code) > 30:
        return {"success": False, "message": "One or more fields exceed the allowed length."}, 400
    duplicate = Society.query.filter(Society.society_code == society_code, Society.society_id != society_id).first()
    if duplicate:
        return {"success": False, "message": "This society code is already in use. Enter a unique code."}, 409

    try:
        society.society_name = society_name
        society.description = description
        society.contact_email = contact_email
        society.contact_phone = contact_phone
        society.society_code = society_code
        # Editing an existing society must not silently unapprove it.
        db.session.commit()
        return {"success": True, "message": "Society updated successfully", "society": _society_admin_dict(society)}, 200
    except Exception as e:
        db.session.rollback()
        return {"success": False, "message": "Failed to update society", "error": str(e)}, 500


def approve_society(society_id):

    society = Society.query.get(society_id)

    if not society:
        return {
            "success": False,
            "message": "Society not found"
        }, 404

    if society.status != "PENDING":
        return {
            "success": False,
            "message": "Only PENDING societies can be approved"
        }, 400

    try:

        # Generate unique Society Code
        society_code = None

        while society_code is None:

            candidate = "SOC-" + token_hex(4).upper()

            existing = Society.query.filter_by(
                society_code=candidate
            ).first()

            if not existing:
                society_code = candidate

        society.status = "APPROVED"
        society.society_code = society_code
        society.rejection_reason = None

        db.session.commit()

        return {
            "success": True,
            "message": "Society approved successfully",
            "society_code": society_code
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to approve society",
            "error": str(e)
        }, 500


def reject_society(society_id, rejection_reason):

    society = Society.query.get(society_id)

    if not society:
        return {
            "success": False,
            "message": "Society not found"
        }, 404

    if society.status != "PENDING":
        return {
            "success": False,
            "message": "Only PENDING societies can be rejected"
        }, 400

    if not rejection_reason:
        return {
            "success": False,
            "message": "Rejection reason is required"
        }, 400

    try:

        society.status = "REJECTED"
        society.rejection_reason = rejection_reason

        db.session.commit()

        return {
            "success": True,
            "message": "Society rejected successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to reject society",
            "error": str(e)
        }, 500


def update_society_status(society_id, status):

    valid_statuses = [
        "APPROVED",
        "REJECTED",
        "INACTIVE"
    ]

    if status not in valid_statuses:
        return {
            "success": False,
            "message": "Invalid society status"
        }, 400

    society = Society.query.get(society_id)

    if not society:
        return {
            "success": False,
            "message": "Society not found"
        }, 404

    try:

        society.status = status

        db.session.commit()

        return {
            "success": True,
            "message": "Society status updated successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update society status",
            "error": str(e)
        }, 500


# =========================================================
# ORGANIZER MANAGEMENT
# =========================================================


def get_all_organizers_for_admin():
    try:
        organizers = OrganizerProfile.query.all()

        return {
            "success": True,
            "organizers": [
                {
                    "organizer_id": organizer.organizer_id,
                    "user_id": organizer.user_id,
                    "name": organizer.user.name if organizer.user else None,
                    "email": organizer.user.email if organizer.user else None,
                    "role": organizer.user.role if organizer.user else None,
                    "account_status": (
                        organizer.user.account_status
                        if organizer.user else None
                    ),
                    "society_id": organizer.society_id,
                    "society_name": (
                        organizer.society.society_name
                        if organizer.society else None
                    ),
                    "society_code": organizer.society_code,
                    "organizer_status": organizer.organizer_status,
                    "date_joined": (
                        organizer.date_joined.isoformat()
                        if organizer.date_joined else None
                    ),
                    "date_updated": (
                        organizer.date_updated.isoformat()
                        if organizer.date_updated else None
                    )
                }
                for organizer in organizers
            ]
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to fetch organizers",
            "error": str(e)
        }, 500

def approve_organizer(organizer_id):

    organizer = OrganizerProfile.query.get(organizer_id)

    if not organizer:
        return {
            "success": False,
            "message": "Organizer profile not found"
        }, 404

    if organizer.organizer_status != "PENDING":
        return {
            "success": False,
            "message": "Only PENDING organizers can be approved"
        }, 400

    try:

        organizer.organizer_status = "APPROVED"
        # Date joined means the date approval became effective; do not overwrite
        # it if an admin retries an operation after a successful approval.
        organizer.date_joined = organizer.date_joined or datetime.utcnow()

        # Make sure the linked user is an ORGANIZER
        user = User.query.get(organizer.user_id)

        if user:
            user.role = "ORGANIZER"

        db.session.commit()

        return {
            "success": True,
            "message": "Organizer approved successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to approve organizer",
            "error": str(e)
        }, 500


def reject_organizer(organizer_id, rejection_reason=None):

    organizer = OrganizerProfile.query.get(organizer_id)

    if not organizer:
        return {
            "success": False,
            "message": "Organizer profile not found"
        }, 404

    if organizer.organizer_status != "PENDING":
        return {
            "success": False,
            "message": "Only PENDING organizers can be rejected"
        }, 400

    try:

        organizer.organizer_status = "REJECTED"

        db.session.commit()

        return {
            "success": True,
            "message": "Organizer rejected successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to reject organizer",
            "error": str(e)
        }, 500



def update_organizer_status(organizer_id, status):

    valid_statuses = [
        "APPROVED",
        "REJECTED",
        "INACTIVE"
    ]

    if status not in valid_statuses:
        return {
            "success": False,
            "message": "Invalid organizer status"
        }, 400

    organizer = OrganizerProfile.query.get(organizer_id)

    if not organizer:
        return {
            "success": False,
        "message": "Organizer profile not found"
        }, 404

    user = User.query.get(organizer.user_id)

    try:
        # Update the organizer profile status
        organizer.organizer_status = status

        # Grant the organizer role only after approval
        if status == "APPROVED":
            if not user:
                return {
                    "success": False,
                    "message": "Associated user not found"
                }, 404

            user.role = "ORGANIZER"

        # If an approved organizer is rejected, restore
        # their participant role.
        elif status == "REJECTED":
            if user and user.role == "ORGANIZER":
                user.role = "PARTICIPANT"

        db.session.commit()

        return {
            "success": True,
            "message": "Organizer status updated successfully",
            "organizer_status": organizer.organizer_status,
            "user_role": user.role if user else None
        }, 200

    except Exception as e:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update organizer status",
            "error": str(e)
        }, 500


# =========================================================
# EVENT MANAGEMENT
# =========================================================

def get_all_events_for_admin():

    try:

        events = Event.query.all()

        return {
            "success": True,
            "events": [
                {
                    "event_id": event.event_id,
                    "organizer_id": event.organizer_id,
                    "event_name": event.event_name,
                    "category": event.category,
                    "event_date": (
                        event.event_date.isoformat()
                        if event.event_date else None
                    ),
                    "start_time": (
                        event.start_time.strftime("%H:%M")
                        if event.start_time else None
                    ),
                    "end_time": (
                        event.end_time.strftime("%H:%M")
                        if event.end_time else None
                    ),
                    "venue_id": event.venue_id,
                    "capacity": event.capacity,
                    "attendance_count": event.attendance_count,
                    "status": event.status,
                    "rejection_reason": event.rejection_reason
                }
                for event in events
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch events",
            "error": str(e)
        }, 500


def approve_event_by_admin(event_id):

    from app.services.event_service import approve_event

    return approve_event(event_id)


def reject_event_by_admin(event_id, rejection_reason):

    from app.services.event_service import reject_event

    return reject_event(
        event_id,
        rejection_reason
    )


# =========================================================
# VENUE MANAGEMENT
# =========================================================

def add_venue(data):

    required_fields = [
        "venue_name",
        "location",
        "capacity"
    ]

    for field in required_fields:

        if field not in data:
            return {
                "success": False,
                "message": f"{field} is required"
            }, 400

    existing = Venue.query.filter_by(
        venue_name=data["venue_name"]
    ).first()

    if existing:
        return {
            "success": False,
            "message": "Venue with this name already exists"
        }, 409

    try:

        venue = Venue(
            venue_name=data["venue_name"],
            location=data["location"],
            capacity=data["capacity"],
            venue_status=data.get(
                "venue_status",
                "ACTIVE"
            ),
            description=data.get("description")
        )

        db.session.add(venue)
        db.session.commit()

        return {
            "success": True,
            "message": "Venue added successfully",
            "venue_id": venue.venue_id
        }, 201

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to add venue",
            "error": str(e)
        }, 500


def update_venue_by_admin(venue_id, data):

    venue = Venue.query.get(venue_id)

    if not venue:
        return {
            "success": False,
            "message": "Venue not found"
        }, 404

    allowed_fields = [
        "venue_name",
        "location",
        "capacity",
        "venue_status",
        "description"
    ]

    try:

        for field in allowed_fields:

            if field in data:
                setattr(
                    venue,
                    field,
                    data[field]
                )

        db.session.commit()

        return {
            "success": True,
            "message": "Venue updated successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update venue",
            "error": str(e)
        }, 500


def disable_venue(venue_id):

    venue = Venue.query.get(venue_id)

    if not venue:
        return {
            "success": False,
            "message": "Venue not found"
        }, 404

    try:

        venue.venue_status = "INACTIVE"

        db.session.commit()

        return {
            "success": True,
            "message": "Venue disabled successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to disable venue",
            "error": str(e)
        }, 500