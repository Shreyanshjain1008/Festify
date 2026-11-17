from datetime import datetime

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from app.extensions import db


class Feedback(db.Model):
    __tablename__ = "feedback"
    __table_args__ = (
        CheckConstraint(
            "rating BETWEEN 1 AND 5",
            name="chk_feedback_rating"
        ),
        UniqueConstraint(
            "event_id",
            "user_id",
            name="uk_feedback_event_user"
        ),
        {
            "schema": "festify"
        }
    )

    feedback_id = db.Column(
        db.BigInteger,
        primary_key=True,
        autoincrement=True
    )

    event_id = db.Column(
        db.BigInteger,
        ForeignKey(
            "festify.events.event_id"
        ),
        nullable=False
    )

    user_id = db.Column(
        db.BigInteger,
        ForeignKey(
            "festify.users.user_id"
        ),
        nullable=False
    )

    rating = db.Column(
        db.SmallInteger,
        nullable=False
    )

    comment = db.Column(
        db.Text,
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
    user = db.relationship(
        "User",
        back_populates="feedbacks"
    )

    event = db.relationship(
        "Event",
        back_populates="feedbacks"
    )

    def __repr__(self):
        return f"<Feedback {self.feedback_id}>"