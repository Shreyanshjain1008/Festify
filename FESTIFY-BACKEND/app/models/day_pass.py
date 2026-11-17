from datetime import datetime
from app.extensions import db

class DayPass(db.Model):
    __tablename__ = "day_passes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "festival_day", name="uq_day_pass_user_day"),
        db.CheckConstraint("festival_day IN ('Day-1', 'Day-2', 'Day-3')", name="chk_day_pass_festival_day"),
        {"schema": "festify"},
    )

    day_pass_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.BigInteger, db.ForeignKey("festify.users.user_id", ondelete="CASCADE"), nullable=False)
    festival_day = db.Column(db.String(10), nullable=False)
    pass_token = db.Column(db.String(128), nullable=False, unique=True)
    status = db.Column(db.String(20), nullable=False, default="ACTIVE")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
