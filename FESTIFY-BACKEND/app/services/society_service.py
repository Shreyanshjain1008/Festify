from app.extensions import db
from app.models.society import Society


def society_to_dict(society):

    return {
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
            if society.date_created
            else None
        ),
        "date_updated": (
            society.date_updated.isoformat()
            if society.date_updated
            else None
        )
    }


# =========================================================
# CREATE SOCIETY REQUEST
# =========================================================

def create_society(data):

    required_fields = [
        "society_name",
        "contact_email",
        "contact_phone"
    ]

    for field in required_fields:

        if field not in data or data[field] is None:

            return {
                "success": False,
                "message": f"{field} is required"
            }, 400

    try:

        society = Society(
            society_name=data["society_name"],
            description=data.get("description"),
            contact_email=data["contact_email"],
            contact_phone=data["contact_phone"],

            # These MUST NOT come from the client.
            # New society always starts as PENDING.
            society_code=None,
            status="PENDING",
            rejection_reason=None
        )

        db.session.add(society)
        db.session.commit()

        return {
            "success": True,
            "message": "Society registration submitted successfully. Waiting for admin approval.",
            "society_id": society.society_id
        }, 201

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to create society",
            "error": str(e)
        }, 500


# =========================================================
# GET ALL SOCIETIES
# =========================================================

def get_all_societies():

    try:

        societies = Society.query.all()

        return {
            "success": True,
            "societies": [
                society_to_dict(society)
                for society in societies
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch societies",
            "error": str(e)
        }, 500


# =========================================================
# GET SOCIETY BY ID
# =========================================================

def get_society_by_id(society_id):

    society = Society.query.get(
        society_id
    )

    if not society:

        return {
            "success": False,
            "message": "Society not found"
        }, 404

    return {
        "success": True,
        "society": society_to_dict(society)
    }, 200


# =========================================================
# UPDATE SOCIETY
# =========================================================

def update_society(society_id, data):

    society = Society.query.get(
        society_id
    )

    if not society:

        return {
            "success": False,
            "message": "Society not found"
        }, 404

    try:

        allowed_fields = [
            "society_name",
            "description",
            "contact_email",
            "contact_phone"
        ]

        for field in allowed_fields:

            if field in data:

                setattr(
                    society,
                    field,
                    data[field]
                )

        db.session.commit()

        return {
            "success": True,
            "message": "Society updated successfully"
        }, 200

    except Exception as e:

        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update society",
            "error": str(e)
        }, 500