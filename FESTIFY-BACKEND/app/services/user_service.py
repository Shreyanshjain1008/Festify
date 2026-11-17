from datetime import datetime

from app.extensions import db
from app.models.user import User


def user_to_dict(user):

    return {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "college_id_number": user.college_id_number,
        "college_name": user.college_name,
        "branch": user.branch,
        "year_of_study": user.year_of_study,
        "date_of_birth": (
            user.date_of_birth.isoformat()
            if user.date_of_birth
            else None
        ),
        "gender": user.gender,
        "role": user.role,
        "account_status": user.account_status,
        "date_created": (
            user.date_created.isoformat()
            if user.date_created
            else None
        )
    }


def get_all_users():

    try:
        users = User.query.all()

        return {
            "success": True,
            "users": [
                user_to_dict(user)
                for user in users
            ]
        }, 200

    except Exception as e:

        return {
            "success": False,
            "message": "Failed to fetch users",
            "error": str(e)
        }, 500


def get_user_by_id(user_id):

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, 404

    return {
        "success": True,
        "user": user_to_dict(user)
    }, 200


def update_user(user_id, data):

    user = User.query.get(user_id)

    if not user:
        return {
            "success": False,
            "message": "User not found"
        }, 404

    try:

        allowed_fields = [
            "name",
            "email",
            "phone",
            "college_id_number",
            "college_name",
            "branch",
            "year_of_study",
            "gender",
            "role",
            "account_status"
        ]

        for field in allowed_fields:
            if field in data:
                setattr(user, field, data[field])

        if "date_of_birth" in data:

            user.date_of_birth = datetime.strptime(
                data["date_of_birth"],
                "%Y-%m-%d"
            ).date()

        db.session.commit()

        return {
            "success": True,
            "message": "User updated successfully"
        }, 200

    except ValueError:
        db.session.rollback()

        return {
            "success": False,
            "message": "date_of_birth must be in YYYY-MM-DD format"
        }, 400

    except Exception as e:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update user",
            "error": str(e)
        }, 500


def update_user_status(user_id, account_status):

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
            "message": "Account status updated successfully"
        }, 200

    except Exception as e:
        db.session.rollback()

        return {
            "success": False,
            "message": "Failed to update account status",
            "error": str(e)
        }, 500


def delete_user(user_id):

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