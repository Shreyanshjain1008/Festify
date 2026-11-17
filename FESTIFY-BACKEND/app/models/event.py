from app.extensions import db
from datetime import datetime


class Event(db.Model):
    __tablename__ = 'events'
    __table_args__ = {'schema': 'festify'}

    event_id = db.Column(db.BigInteger, primary_key=True)

    organizer_id = db.Column(
        db.BigInteger,
        db.ForeignKey('festify.organizer_profiles.organizer_id'),
        nullable=False
    )

    event_name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    fest_day = db.Column(db.String(10), nullable=False, default='Day-1')
    event_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    venue_id = db.Column(
        db.BigInteger,
        db.ForeignKey('festify.venues.venue_id'),
        nullable=True
    )

    capacity = db.Column(db.Integer, nullable=False)
    eligibility = db.Column(db.String(500), nullable=True)
    rules = db.Column(db.Text, nullable=True)
    registration_deadline = db.Column(db.DateTime, nullable=False)
    event_image = db.Column(db.String(500), nullable=True)
    attendance_count = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default='DRAFT')
    rejection_reason = db.Column(db.String(500), nullable=True)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    registrations = db.relationship('EventRegistration', back_populates='event')
    custom_fields = db.relationship('EventCustomField', back_populates='event')
    feedbacks = db.relationship('Feedback', back_populates='event')

    def __repr__(self):
        return f"<Event {self.event_name} ({self.status})>"