from . import db


class Club(db.Model):
    __tablename__ = "clubs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    league = db.Column(db.String(64), nullable=False)
    country = db.Column(db.String(64), nullable=False)
    stadium = db.Column(db.String(128))
    stadium_capacity = db.Column(db.Integer)

    overall_rating = db.Column(db.Integer)  # 1-100
    prestige = db.Column(db.Integer)  # 1-5 stars

    transfer_budget = db.Column(db.Float, default=0.0)
    wage_budget = db.Column(db.Float, default=0.0)

    board_ambition = db.Column(db.String(32))  # title/top4/mid-table/survival

    board_confidence = db.Column(db.Integer, default=50)  # 0-100
    manager_id = db.Column(db.Integer, db.ForeignKey("managers.id"))

    players = db.relationship("Player", back_populates="club", lazy="dynamic")
    home_fixtures = db.relationship(
        "Fixture",
        foreign_keys="Fixture.home_club_id",
        back_populates="home_club",
        lazy="dynamic",
    )
    away_fixtures = db.relationship(
        "Fixture",
        foreign_keys="Fixture.away_club_id",
        back_populates="away_club",
        lazy="dynamic",
    )
    standings = db.relationship("Standing", back_populates="club", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Club {self.name} ({self.league})>"

