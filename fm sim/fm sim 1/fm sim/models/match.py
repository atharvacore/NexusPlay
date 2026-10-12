from datetime import datetime

from . import db


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    fixture_id = db.Column(db.Integer, db.ForeignKey("fixtures.id"), nullable=False)

    home_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    away_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

    home_goals = db.Column(db.Integer, default=0)
    away_goals = db.Column(db.Integer, default=0)

    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

    events = db.relationship("MatchEvent", back_populates="match", lazy="dynamic")


class MatchEvent(db.Model):
    __tablename__ = "match_events"

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)

    minute = db.Column(db.Integer, nullable=False)
    event_type = db.Column(
        db.String(16), nullable=False
    )  # goal/yellow/red/sub/chance/etc.
    player_id = db.Column(db.Integer, db.ForeignKey("players.id"), nullable=True)
    description = db.Column(db.String(256))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    match = db.relationship("Match", back_populates="events")

