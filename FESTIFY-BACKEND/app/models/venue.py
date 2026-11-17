from datetime import datetime

from sqlalchemy import CheckConstraint
from app.extensions import db


class Venue(db.Model):
    __tablename__ = "venues"
    __table_args__ = (
        CheckConstraint(
            "capacity > 0",
            name="chk_venue_capacity"
        ),
        CheckConstraint(
            "venue_status IN ('ACTIVE', 'INACTIVE')",
            name="chk_venue_status"
        ),
        {
            "schema": "festify"
        }
    )

    venue_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    venue_name = db.Column(
        db.String(150),
        nullable=False,
        unique=True
    )

    location = db.Column(
        db.String(255),
        nullable=True
    )

    capacity = db.Column(
        db.Integer,
        nullable=False
    )

    venue_status = db.Column(
        db.String(20),
        nullable=False,
        default="ACTIVE"
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    date_updated = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<Venue {self.venue_id}: {self.venue_name}>"