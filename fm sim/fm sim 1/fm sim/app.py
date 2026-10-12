from flask import Flask
import os
import webbrowser
from threading import Timer
from config import get_config
from models import db
from routes import register_routes

def create_app():
    app = Flask(__name__)
    app_config = get_config()
    app.config.from_object(app_config)
    db.init_app(app)
    register_routes(app)

    with app.app_context():
        db.create_all()
        from models.club import Club
        if Club.query.count() == 0:
            from data.seed_data import seed_all
            seed_all()

    return app

app = create_app()

@app.before_request
def restore_session():
    from flask import session
    if 'club_id' not in session:
        try:
            from models.game_state import GameState
            import json
            
            club_id_state = GameState.query.filter_by(
                key='last_club_id').first()
            if club_id_state and club_id_state.value:
                club_id = int(club_id_state.value)
                from models.club import Club
                club = Club.query.get(club_id)
                if club:
                    session['club_id'] = club_id
                    
                    # Restore formation
                    form_state = GameState.query.filter_by(
                        key='last_formation').first()
                    if form_state and form_state.value:
                        session['formation'] = form_state.value
                    
                    # Restore starting 11
                    xi_state = GameState.query.filter_by(
                        key='last_starting_11').first()
                    if xi_state and xi_state.value:
                        try:
                            session['starting_11'] = json.loads(
                                xi_state.value)
                        except:
                            pass
                    
                    session.modified = True
                    print(f"Session restored for club: {club.name}")
        except Exception as e:
            print(f"Session restore error: {e}")

@app.route('/admin/fix-nationalities')
def fix_nationalities():
    from data.seed_data import get_nationality, REAL_PLAYER_NATIONALITIES
    from models.player import Player
    from models.club import Club
    players = Player.query.all()
    fixed = 0
    for player in players:
        needs_fix = (
            not player.nationality or 
            player.nationality.strip() == '' or 
            player.nationality == 'Unknown' or
            player.nationality == 'None'
        )
        if needs_fix:
            if player.name in REAL_PLAYER_NATIONALITIES:
                player.nationality = REAL_PLAYER_NATIONALITIES[player.name]
            else:
                club = Club.query.get(player.club_id)
                league = club.league if club else None
                player.nationality = get_nationality(league)
            fixed += 1
    db.session.commit()
    return f"Fixed {fixed} players nationality. <a href='/'>Go home</a>"


if __name__ == "__main__":
    # Only auto-open browser when launched directly, not from the portal
    if not os.environ.get('LAUNCHED_FROM_PORTAL'):
        def open_browser():
            webbrowser.open("http://127.0.0.1:5000/")
        Timer(1.5, open_browser).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
