from datetime import datetime

from sqlalchemy import CheckConstraint
from app.extensions import db


class Society(db.Model):
    __tablename__ = "societies"
    __table_args__ = (
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'INACTIVE')",
            name="chk_societies_status"
        ),
        {
            "schema": "festify"
        }
    )

    society_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    society_name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.String(500),
        nullable=True
    )

    contact_email = db.Column(
        db.String(150),
        nullable=False
    )

    contact_phone = db.Column(
        db.String(15),
        nullable=False
    )

    society_code = db.Column(
        db.String(30),
        unique=True,
        nullable=True
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="PENDING"
    )

    rejection_reason = db.Column(
        db.String(500),
        nullable=True
    )

    date_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    date_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    organizers = db.relationship(
        "OrganizerProfile",
        back_populates="society"
    )

    def __repr__(self):
        return f"<Society {self.society_id}: {self.society_name}>"