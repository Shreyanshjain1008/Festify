from app.extensions import db
from datetime import datetime


class EventCustomField(db.Model):
    __tablename__ = 'event_custom_fields'
    __table_args__ = {'schema': 'festify'}

    custom_field_id = db.Column(db.BigInteger, primary_key=True)

    event_id = db.Column(
        db.BigInteger,
        db.ForeignKey('festify.events.event_id'),
        nullable=False
    )

    field_name = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(20), nullable=False)
    is_required = db.Column(db.Boolean, nullable=False, default=False)
    field_options = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, nullable=True)

    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    event = db.relationship('Event', back_populates='custom_fields')
    submitted_values = db.relationship('EventRegistrationCustomValue', back_populates='custom_field')

    def __repr__(self):
        return f"<CustomField {self.field_name} ({self.field_type})>"