from datetime import date

from . import db


class Season(db.Model):
    __tablename__ = "seasons"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    league = db.Column(db.String(64), nullable=False)

    fixtures = db.relationship("Fixture", back_populates="season", lazy="dynamic")
    standings = db.relationship("Standing", back_populates="season", lazy="dynamic")


class Fixture(db.Model):
    __tablename__ = "fixtures"

    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.id"), nullable=False)
    home_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)
    away_club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

    home_score = db.Column(db.Integer, default=0)
    away_score = db.Column(db.Integer, default=0)

    match_date = db.Column(db.Date, default=date.today)
    played = db.Column(db.Boolean, default=False)

    season = db.relationship("Season", back_populates="fixtures")
    home_club = db.relationship(
        "Club", foreign_keys=[home_club_id], back_populates="home_fixtures"
    )
    away_club = db.relationship(
        "Club", foreign_keys=[away_club_id], back_populates="away_fixtures"
    )


class Standing(db.Model):
    __tablename__ = "standings"

    id = db.Column(db.Integer, primary_key=True)
    season_id = db.Column(db.Integer, db.ForeignKey("seasons.id"), nullable=False)
    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"), nullable=False)

    played = db.Column(db.Integer, default=0)
    won = db.Column(db.Integer, default=0)
    drawn = db.Column(db.Integer, default=0)
    lost = db.Column(db.Integer, default=0)

    gf = db.Column(db.Integer, default=0)  # goals for
    ga = db.Column(db.Integer, default=0)  # goals against
    gd = db.Column(db.Integer, default=0)  # goal difference
    points = db.Column(db.Integer, default=0)

    season = db.relationship("Season", back_populates="standings")
    club = db.relationship("Club", back_populates="standings")

