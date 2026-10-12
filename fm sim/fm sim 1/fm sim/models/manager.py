from . import db


class Manager(db.Model):
    __tablename__ = "managers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    reputation = db.Column(db.Integer, default=50)  # 1-100

    preferred_formation = db.Column(db.String(16), default="4-3-3")
    preferred_style = db.Column(db.String(32), default="balanced")

    club = db.relationship("Club", backref="manager", uselist=False)

    def __repr__(self) -> str:
        return f"<Manager {self.name}>"

