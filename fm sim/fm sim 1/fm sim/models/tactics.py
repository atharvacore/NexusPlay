from models import db

class TacticsSetup(db.Model):
    __tablename__ = 'tactics_setup'
    id = db.Column(db.Integer, primary_key=True)
    club_id = db.Column(db.Integer, db.ForeignKey('clubs.id'))
    formation = db.Column(db.String(10), default='4-3-3')
    mentality = db.Column(db.String(20), default='Balanced')
    pressing = db.Column(db.String(20), default='Medium')
    starting_xi_ids = db.Column(db.Text, default='[]')
