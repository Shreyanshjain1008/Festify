
import re
from datetime import date, datetime
from app.utils.otp import (
    is_email_verified,
    clear_email_verification,
)
import bcrypt
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.extensions import db
from app.models.user import User
from app.models.society import Society
from app.models.organizer_profile import OrganizerProfile
from app.utils.token import generate_token


def _required_text(data, field):
    value = data.get(field)

    if value is None or not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} is required")

    return value.strip()


def _parse_registration(data):
    name = _required_text(data, "name")
    email = _required_text(data, "email").lower()
    password = _required_text(data, "password")
    phone = _required_text(data, "phone")
    college_id_number = _required_text(data, "college_id_number")
    college_name = _required_text(data, "college_name")
    branch = _required_text(data, "branch")
    gender = _required_text(data, "gender")
    dob_text = _required_text(data, "date_of_birth")

    if len(name) > 100:
        raise ValueError("Name must be 100 characters or fewer")

    if len(email) > 150 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Please enter a valid email address")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")

    if len(phone) > 15:
        raise ValueError("Phone number must be 15 characters or fewer")

    if len(college_id_number) > 50:
        raise ValueError("Enrollment number must be 50 characters or fewer")

    if len(college_name) > 150:
        raise ValueError("College name must be 150 characters or fewer")

    if len(branch) > 100:
        raise ValueError("Branch must be 100 characters or fewer")

    try:
        year_of_study = int(data.get("year_of_study"))
    except (TypeError, ValueError):
        raise ValueError("year_of_study must be a number between 1 and 5")

    if year_of_study not in range(1, 6):
        raise ValueError("year_of_study must be between 1 and 5")

    try:
        date_of_birth = date.fromisoformat(dob_text)
    except (ValueError, TypeError):
        raise ValueError("date_of_birth must be in YYYY-MM-DD format")

    if date_of_birth >= date.today():
        raise ValueError("Date of birth must be in the past")

    if len(gender) > 20:
        raise ValueError("Gender must be 20 characters or fewer")

    return {
        "name": name,
        "email": email,
        "password": password,
        "phone": phone,
        "college_id_number": college_id_number,
        "college_name": college_name,
        "branch": branch,
        "year_of_study": year_of_study,
        "date_of_birth": date_of_birth,
        "gender": gender,
    }


def register_user(data):
    if not isinstance(data, dict):
        return {"success": False, "message": "Invalid request body"}, 400

    try:
        fields = _parse_registration(data)
        if not is_email_verified(fields["email"]):
            return {
                "success": False,
                "message": "Please verify your email before signing up.",
            }, 403
        role = str(data.get("role", "PARTICIPANT")).strip().upper()

        if role not in ("PARTICIPANT", "ORGANIZER"):
            return {
                "success": False,
                "message": "Invalid registration role",
            }, 400

        society_name = None
        society_code = None

        if role == "ORGANIZER":
            society_name = _required_text(data, "society_name")
            society_code = _required_text(data, "society_code")

            if len(society_name) > 150:
                raise ValueError("Society name must be 150 characters or fewer")

            if len(society_code) > 30:
                raise ValueError("Society code must be 30 characters or fewer")

        if User.query.filter_by(email=fields["email"]).first():
            return {
                "success": False,
                "message": "Email already registered",
            }, 409

        if User.query.filter_by(
            college_id_number=fields["college_id_number"]
        ).first():
            return {
                "success": False,
                "message": "College ID number already registered",
            }, 409

        password_hash = bcrypt.hashpw(
            fields["password"].encode("utf-8"),
            bcrypt.gensalt(),
        ).decode("utf-8")

        user = User(
            name=fields["name"],
            email=fields["email"],
            password_hash=password_hash,
            phone=fields["phone"],
            college_id_number=fields["college_id_number"],
            college_name=fields["college_name"],
            branch=fields["branch"],
            year_of_study=fields["year_of_study"],
            date_of_birth=fields["date_of_birth"],
            gender=fields["gender"],
            role=role,
            account_status="ACTIVE",
        )

        db.session.add(user)
        db.session.flush()

        response = {
            "success": True,
            "message": (
                "Student registered successfully"
                if role == "PARTICIPANT"
                else "Organizer registration submitted for approval"
            ),
            "user_id": user.user_id,
            "role": role,
        }

        if role == "ORGANIZER":
            # Reuse a society with this assigned code, if it already exists.
            society = Society.query.filter_by(
                society_code=society_code
            ).first()

            if society:
                if society.society_name.strip().casefold() != society_name.casefold():
                    db.session.rollback()
                    return {
                        "success": False,
                        "message": (
                            "This society code is already assigned to a "
                            "different society. Please check the code."
                        ),
                    }, 409

                if society.status in ("REJECTED", "INACTIVE"):
                    db.session.rollback()
                    return {
                        "success": False,
                        "message": (
                            "This society is not currently accepting "
                            "organizer registrations."
                        ),
                    }, 409
            else:
                society = Society(
                    society_name=society_name,
                    description=None,
                    contact_email=fields["email"],
                    contact_phone=fields["phone"],
                    society_code=society_code,
                    status="PENDING",
                )
                db.session.add(society)
                db.session.flush()

            profile = OrganizerProfile(
                user_id=user.user_id,
                society_id=society.society_id,
                society_code=society_code,
                organizer_status="PENDING",
                date_joined=datetime.utcnow(),
            )

            db.session.add(profile)
            response["society_id"] = society.society_id
            response["organizer_status"] = "PENDING"

        # Save all related records together.
        db.session.commit()
        clear_email_verification(fields["email"])
        return response, 201

    except ValueError as exc:
        db.session.rollback()
        return {"success": False, "message": str(exc)}, 400

    except IntegrityError:
        db.session.rollback()
        return {
            "success": False,
            "message": (
                "A duplicate email, college ID, society code, or conflicting "
                "record was detected. Please check your details and try again."
            ),
        }, 409

    except SQLAlchemyError:
        db.session.rollback()
        return {
            "success": False,
            "message": (
                "Database operation failed. Check your database connection "
                "and verify that the Festify tables exist."
            ),
        }, 500

    except Exception:
        db.session.rollback()
        return {
            "success": False,
            "message": "Registration failed due to a server error.",
        }, 500



def login_user(email, password):
    if not email or not password:
        return {
            "success": False,
            "message": "Email and password are required",
        }, 400

    email = email.strip().lower()
    user = User.query.filter_by(email=email).first()

    if not user or not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password_hash.encode("utf-8"),
    ):
        return {
            "success": False,
            "message": "Invalid email or password",
        }, 401

    if user.account_status != "ACTIVE":
        return {
            "success": False,
            "message": "Account is not active",
        }, 403

    token = generate_token(user)

    
    user_data = {
        "user_id": user.user_id,
        "name": user.name,
        "email": user.email,
        "role": user.role
    }

    if user.role == "ORGANIZER":
        from app.models.organizer_profile import OrganizerProfile

        organizer = OrganizerProfile.query.filter_by(
            user_id=user.user_id
        ).first()

        if not organizer:
            return {
                "success": False,
                "message": "Organizer profile not found. Please contact the administrator."
            }, 403

        if organizer.organizer_status != "APPROVED":
            return {
                "success": False,
                "message": "Your organizer account has not been approved."
            }, 403

        user_data["organizer_id"] = organizer.organizer_id
        user_data["society_id"] = organizer.society_id
        user_data["organizer_status"] = organizer.organizer_status

    token = generate_token(user)

    return {
        "success": True,
        "message": "Login successful",
        "token": token,
        "user": user_data
    }, 200

