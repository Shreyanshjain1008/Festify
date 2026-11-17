from datetime import datetime

from app.extensions import db
from app.models.organizer_profile import OrganizerProfile
from app.models.user import User
from app.models.society import Society


def organizer_to_dict(organizer):

    return {
        "organizer_id": organizer.organizer_id,
        "user_id": organizer.user_id,
        "society_id": organizer.society_id,
        "organizer_status": organizer.organizer_status,
        "date_joined": (
            organizer.date_joined.isoformat()
            if organizer.date_joined
            else None
        ),
        "date_updated": (
            organizer.date_updated.isoformat()
            if organizer.date_updated
            else None
        )
    }


def create_organizer(data):

    # ---------------------------------------------------------
    # Required fields
    # ---------------------------------------------------------

    required_fields = [
        "user_id",
        "society_code"
    ]

    for field in required_fields:

        if field not in data or data[field] is None:
            return {
                "success": False,
                "message": f"{field} is required"
            }, 400

    user_id = data["user_id"]
    society_code = data["society_code"]

    # ---------------------------------------------------------
    # Check user
    # ---------------------------------------------------------

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, 404

    # ---------------------------------------------------------
    # Check if user already has organizer profile
    # ---------------------------------------------------------

    existing_organizer = OrganizerProfile.query.filter_by(
        user_id=user_id
    ).first()

    if existing_organizer:

        return {
            "success": False,
            "message": "User already has an organizer profile"
        }, 409

    # ---------------------------------------------------------
    # Find approved society using Society Code
    # ---------------------------------------------------------

    society = Society.query.filter_by(
        society_code=society_code,
        status="APPROVED"
    ).first()

    if not society:

        return {
            "success": False,
            "message": "Invalid or unapproved Society Code"
        }, 400

    # ---------------------------------------------------------
    # MAXIMUM 4 ORGANIZERS PER SOCIETY
    # ---------------------------------------------------------

    organizer_count = OrganizerProfile.query.filter(
        OrganizerProfile.society_id == society.society_id,
        OrganizerProfile.organizer_status.in_(
            ["PENDING", "APPROVED"]
        )
    ).count()

    if organizer_count >= 4:

        return {
            "success": False,
            "message": "This society already has the maximum of 4 organizers"
        }, 409

    # ---------------------------------------------------------
    # Create organizer profile
    # ---------------------------------------------------------

    try:

        organizer = OrganizerProfile(
            user_id=user_id,
            society_id=society.society_id,
            society_code=society_code,
            organizer_status="PENDING"
        )

        db.session.add(organizer)
        db.session.commit()

        return {
            "success": True,
            "message": "Organizer registration submitted successfully. Waiting for admin approval.",
            "organizer_id": organizer.organizer_id
        }, 201

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to create organizer profile",
            "error": str(e)
        }, 500


def get_all_organizers():

    try:

        organizers = OrganizerProfile.query.all()

        return {
            "success": True,
            "organizers": [
                organizer_to_dict(organizer)
                for organizer in organizers
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch organizers",
            "error": str(e)
        }, 500


def get_organizer_by_id(organizer_id):

    organizer = OrganizerProfile.query.get(organizer_id)

    if not organizer:

        return {
            "success": False,
            "message": "Organizer profile not found"
        }, 404

    return {
        "success": True,
        "organizer": organizer_to_dict(organizer)
    }, 200


def update_organizer(organizer_id, data):

    organizer = OrganizerProfile.query.get(organizer_id)

    if not organizer:

        return {
            "success": False,
            "message": "Organizer profile not found"
        }, 404

    try:

        # -----------------------------------------------------
        # Only basic organizer information can be updated here.
        #
        # Status is NOT updated here.
        # Society approval/rejection is NOT handled here.
        # Admin handles those operations.
        # -----------------------------------------------------

        if "user_id" in data:

            new_user_id = data["user_id"]

            user = User.query.get(new_user_id)

            if not user:

                return {
                    "success": False,
                    "message": "User not found"
                }, 404

            existing = OrganizerProfile.query.filter(
                OrganizerProfile.user_id == new_user_id,
                OrganizerProfile.organizer_id != organizer_id
            ).first()

            if existing:

                return {
                    "success": False,
                    "message": "User already has another organizer profile"
                }, 409

            organizer.user_id = new_user_id

        # -----------------------------------------------------
        # Society ID can be updated only if required internally.
        # Society Code is NOT stored in organizer_profiles.
        # -----------------------------------------------------

        if "society_id" in data:

            society = Society.query.get(
                data["society_id"]
            )

            if not society:

                return {
                    "success": False,
                    "message": "Society not found"
                }, 404

            if society.status != "APPROVED":

                return {
                    "success": False,
                    "message": "Organizer can only belong to an approved society"
                }, 400

            organizer.society_id = society.society_id

        # -----------------------------------------------------
        # Date joined
        # -----------------------------------------------------

        if "date_joined" in data:

            try:

                organizer.date_joined = datetime.strptime(
                    data["date_joined"],
                    "%Y-%m-%d %H:%M:%S"
                )

            except ValueError:

                return {
                    "success": False,
                    "message": "date_joined must be in YYYY-MM-DD HH:MM:SS format"
                }, 400

        db.session.commit()

        return {
            "success": True,
            "message": "Organizer profile updated successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update organizer profile",
            "error": str(e)
        }, 500