from datetime import datetime, date as date_cls
from app.extensions import db

DAY_TO_DATE = {
    "Day-1": date_cls(2026, 11, 28),
    "Day-2": date_cls(2026, 11, 29),
    "Day-3": date_cls(2026, 11, 30),
}
FESTIVAL_DATES = {d: day for day, d in DAY_TO_DATE.items()}

class FestPass(db.Model):
    __tablename__ = 'fest_passes'
    __table_args__ = (
        db.UniqueConstraint('user_id', 'fest_date', name='uk_user_fest_date'),
        {'schema': 'festify'}
    )
    fest_pass_id = db.Column(db.BigInteger, primary_key=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey('festify.users.user_id'), nullable=False)
    fest_date = db.Column(db.Date, nullable=False)
    festival_day = db.Column(db.String(10), nullable=True)
    pass_token = db.Column(db.String(255), nullable=False, unique=True)
    pass_status = db.Column(db.String(20), nullable=False, default='ACTIVE')
    issued_at = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', back_populates='fest_passes')

    @property
    def day_label(self):
        return self.festival_day or FESTIVAL_DATES.get(self.fest_date, self.fest_date.isoformat() if self.fest_date else None)

    def __repr__(self):
        return f"<FestPass user={self.user_id} date={self.fest_date} status={self.pass_status}>"
