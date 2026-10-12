from datetime import date

from . import db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    nationality = db.Column(db.String(64))
    age = db.Column(db.Integer)
    position = db.Column(
        db.String(8)
    )  # GK/CB/RB/LB/CM/CAM/CDM/LW/RW/ST etc.

    overall = db.Column(db.Integer)
    pace = db.Column(db.Integer)
    shooting = db.Column(db.Integer)
    passing = db.Column(db.Integer)
    dribbling = db.Column(db.Integer)
    defending = db.Column(db.Integer)
    physical = db.Column(db.Integer)

    potential = db.Column(db.Integer)
    current_ability = db.Column(db.Integer)
    morale = db.Column(db.Integer)  # 1-100

    wage_per_week = db.Column(db.Float)
    contract_end_date = db.Column(db.Date)
    release_clause = db.Column(db.Float)

    club_id = db.Column(db.Integer, db.ForeignKey("clubs.id"))
    club = db.relationship("Club", back_populates="players")

    is_injured = db.Column(db.Boolean, default=False)
    injury_return_date = db.Column(db.Date, default=None)
    is_captain = db.Column(db.Boolean, default=False)

    def years_left_on_contract(self) -> int:
        if not self.contract_end_date:
            return 0
        today = date.today()
        return max(0, self.contract_end_date.year - today.year)

    def __repr__(self) -> str:
        return f"<Player {self.name} ({self.position}) {self.overall}>"

