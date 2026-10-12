from datetime import date
from . import db

class InboxMessage(db.Model):
    __tablename__ = "inbox_messages"

    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    
    subject = db.Column(db.String(128), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    date_sent = db.Column(db.Date, default=date.today)

    club = db.relationship("Club", backref="inbox_messages")
