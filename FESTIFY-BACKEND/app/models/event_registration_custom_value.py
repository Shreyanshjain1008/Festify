from app.extensions import db


class EventRegistrationCustomValue(db.Model):
    __tablename__ = 'event_registration_custom_values'
    __table_args__ = (
        db.UniqueConstraint('registration_id', 'custom_field_id', name='uk_registration_custom_field'),
        {'schema': 'festify'}
    )

    value_id = db.Column(db.BigInteger, primary_key=True)

    registration_id = db.Column(
        db.BigInteger,
        db.ForeignKey('festify.event_registrations.registration_id'),
        nullable=False
    )

    custom_field_id = db.Column(
        db.BigInteger,
        db.ForeignKey('festify.event_custom_fields.custom_field_id'),
        nullable=False
    )

    field_value = db.Column(db.Text, nullable=True)

    registration = db.relationship('EventRegistration', back_populates='custom_values')
    custom_field = db.relationship('EventCustomField', back_populates='submitted_values')

    def __repr__(self):
        return f"<CustomValue reg={self.registration_id} field={self.custom_field_id}>"