
from app.extensions import db
from app.models.venue import Venue


def venue_to_dict(venue):
    return {
        "venue_id": venue.venue_id,
        "venue_name": venue.venue_name,
        "location": venue.location,
        "capacity": venue.capacity,
        "venue_status": venue.venue_status,
        "description": venue.description,
        "date_updated": (
            venue.date_updated.isoformat()
            if venue.date_updated else None
        )
    }


def create_venue(data):
    required_fields = ["venue_name", "capacity"]

    for field in required_fields:
        if field not in data:
            return {
                "success": False,
                "message": f"{field} is required"
            }, 400

    try:
        capacity = int(data["capacity"])
        if capacity <= 0:
            return {
                "success": False,
                "message": "Capacity must be greater than zero"
            }, 400

        venue = Venue(
            venue_name=data["venue_name"].strip(),
            location=data.get("location"),
            capacity=capacity,
            venue_status=data.get("venue_status", "ACTIVE"),
            description=data.get("description")
        )

        db.session.add(venue)
        db.session.commit()

        return {
            "success": True,
            "message": "Venue created successfully",
            "venue_id": venue.venue_id
        }, 201

    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": "Failed to create venue",
            "error": str(e)
        }, 500


def get_all_venues():
    try:
        venues = Venue.query.order_by(Venue.venue_name.asc()).all()
        return {
            "success": True,
            "venues": [venue_to_dict(v) for v in venues]
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to fetch venues",
            "error": str(e)
        }, 500


def get_active_venues():
    try:
        venues = (
            Venue.query
            .filter_by(venue_status="ACTIVE")
            .order_by(Venue.venue_name.asc())
            .all()
        )

        return {
            "success": True,
            "venues": [venue_to_dict(v) for v in venues]
        }, 200

    except Exception as e:
        return {
            "success": False,
            "message": "Failed to fetch active venues",
            "error": str(e)
        }, 500


def get_venue_by_id(venue_id):
    venue = db.session.get(Venue, venue_id)

    if not venue:
        return {
            "success": False,
            "message": "Venue not found"
        }, 404

    return {
        "success": True,
        "venue": venue_to_dict(venue)
    }, 200


def update_venue(venue_id, data):
    venue = db.session.get(Venue, venue_id)

    if not venue:
        return {
            "success": False,
            "message": "Venue not found"
        }, 404

    try:
        if "venue_name" in data:
            venue.venue_name = data["venue_name"].strip()

        if "location" in data:
            venue.location = data["location"]

        if "capacity" in data:
            capacity = int(data["capacity"])
            if capacity <= 0:
                return {
                    "success": False,
                    "message": "Capacity must be greater than zero"
                }, 400
            venue.capacity = capacity

        if "venue_status" in data:
            if data["venue_status"] not in ("ACTIVE", "INACTIVE"):
                return {
                    "success": False,
                    "message": "Invalid venue status"
                }, 400
            venue.venue_status = data["venue_status"]

        if "description" in data:
            venue.description = data["description"]

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


def delete_venue(venue_id):
    venue = db.session.get(Venue, venue_id)

    if not venue:
        return {
            "success": False,
            "message": "Venue not found"
        }, 404

    try:
        db.session.delete(venue)
        db.session.commit()

        return {
            "success": True,
            "message": "Venue deleted successfully"
        }, 200

    except Exception as e:
        db.session.rollback()
        return {
            "success": False,
            "message": (
                "Venue could not be deleted. "
                "It may be referenced by an event."
            ),
            "error": str(e)
        }, 409
