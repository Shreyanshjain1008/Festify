from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, Sequence
from app.extensions import db


class OrganizerProfile(db.Model):
    __tablename__ = "organizer_profiles"

    __table_args__ = (
        CheckConstraint(
            "organizer_status IN "
            "('PENDING', 'APPROVED', 'REJECTED', 'INACTIVE')",
            name="chk_organizer_status"
        ),
        {
            "schema": "festify"
        }
    )

    organizer_id = db.Column(
        db.BigInteger,
        Sequence(
            "organizer_profile_organizer_id_seq",
            schema="festify"
        ),
        primary_key=True,
        nullable=False
    )

    user_id = db.Column(
        db.BigInteger,
        ForeignKey(
            "festify.users.user_id",
            name="fk_organizer_user"
        ),
        nullable=False,
        unique=True
    )

    society_id = db.Column(
        db.BigInteger,
        ForeignKey(
            "festify.societies.society_id",
            name="fk_organizer_society"
        ),
        nullable=False
    )

    society_code = db.Column(
        db.String(50),
        nullable=False
    )

    organizer_status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING"
    )

    date_joined = db.Column(
        db.DateTime,
        nullable=True
    )

    date_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    user = db.relationship(
        "User",
        back_populates="organizer_profile"
    )

    society = db.relationship(
        "Society",
        back_populates="organizers"
    )

    def __repr__(self):
        return f"<OrganizerProfile {self.organizer_id}>"