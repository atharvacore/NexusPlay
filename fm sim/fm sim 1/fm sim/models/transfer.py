from datetime import datetime

from . import db


class Transfer(db.Model):
    __tablename__ = "transfers"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)

    from_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    to_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=True)

    fee = db.Column(db.Float, default=0.0)
    transfer_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(16), default="pending"
    )  # pending/accepted/rejected


class Contract(db.Model):
    __tablename__ = "contracts"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

    wage_per_week = db.Column(db.Float, default=0.0)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    release_clause = db.Column(db.Float, default=0.0)


class Bid(db.Model):
    __tablename__ = "bids"

    id = db.Column(db.Integer, primary_key=True)
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=False)
    from_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    to_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

    offered_fee = db.Column(db.Float, default=0.0)
    offered_wage = db.Column(db.Float, default=0.0)
    is_loan = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(
        db.String(16), default="pending"
    )  # pending/accepted/rejected/countered

