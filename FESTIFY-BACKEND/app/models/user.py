from datetime import datetime

from sqlalchemy import CheckConstraint
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    __table_args__ = (
        CheckConstraint(
            "role IN ('PARTICIPANT', 'ORGANIZER', 'ADMIN', 'SUPER_ADMIN')",
            name="chk_users_role"
        ),
        CheckConstraint(
            "account_status IN ('ACTIVE', 'INACTIVE', 'BLOCKED')",
            name="chk_users_account_status"
        ),
        CheckConstraint(
            "year_of_study > 0",
            name="chk_users_year_of_study"
        ),
        {
            "schema": "festify"
        }
    )

    user_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    college_id_number = db.Column(db.String(50), nullable=False, unique=True)
    college_name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    year_of_study = db.Column(db.SmallInteger, nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="PARTICIPANT")
    account_status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organizer_profile = db.relationship("OrganizerProfile", back_populates="user", uselist=False)
    feedbacks = db.relationship("Feedback", back_populates="user")
    fest_passes = db.relationship("FestPass", back_populates="user")

    def __repr__(self):
        return f"<User {self.user_id}: {self.email}>"