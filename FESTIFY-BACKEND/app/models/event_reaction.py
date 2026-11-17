from datetime import datetime
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from app.extensions import db


class EventReaction(db.Model):
    __tablename__ = "event_reactions"
    __table_args__ = (
        CheckConstraint("reaction IN ('LIKE', 'DISLIKE')", name="chk_event_reaction_value"),
        UniqueConstraint("event_id", "user_id", name="uq_event_reaction_user_event"),
        {"schema": "festify"},
    )

    reaction_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    event_id = db.Column(db.BigInteger, ForeignKey("festify.events.event_id", ondelete="CASCADE"), nullable=False)
    user_id = db.Column(db.BigInteger, ForeignKey("festify.users.user_id", ondelete="CASCADE"), nullable=False)
    reaction = db.Column(db.String(10), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
