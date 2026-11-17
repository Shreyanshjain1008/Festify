from datetime import datetime
from app.extensions import db


class EventRegistration(db.Model):
    __tablename__ = "event_registrations"
    __table_args__ = (
        db.UniqueConstraint("event_id", "user_id", "event_day", name="uk_event_user_day_registration"),
        {"schema": "festify"},
    )

    registration_id = db.Column(db.BigInteger, primary_key=True)
    event_id = db.Column(db.BigInteger, db.ForeignKey("festify.events.event_id"), nullable=False)
    user_id = db.Column(db.BigInteger, db.ForeignKey("festify.users.user_id"), nullable=False)
    # The day is event metadata; campus QR passes are stored separately in fest_passes/day-pass tables.
    event_day = db.Column(db.String(20), nullable=False, default="Day-1")
    registration_status = db.Column(db.String(20), nullable=False, default="CONFIRMED")
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)

    event = db.relationship("Event", back_populates="registrations")
    custom_values = db.relationship("EventRegistrationCustomValue", back_populates="registration")

    def __repr__(self):
        return f"<Registration event={self.event_id} user={self.user_id} day={self.event_day}>"
