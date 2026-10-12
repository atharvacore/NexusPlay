import random
import time
from flask import Blueprint, render_template, abort, request, jsonify, session, redirect, url_for
from models import Club, Player, db, Fixture, Standing, Season

main_bp = Blueprint("main", __name__)

from models.game_state import GameState
from datetime import datetime

def save_game_state(key, value):
    state = GameState.query.filter_by(key=key).first()
    if not state:
        state = GameState(key=key)
        db.session.add(state)
    state.value = str(value)
    state.updated_at = datetime.utcnow()
    db.session.commit()

def load_game_state(key):
    state = GameState.query.filter_by(key=key).first()
    return state.value if state else None
def get_player_club():
    if 'club_id' in session:
        return Club.query.get(session['club_id'])
    return None

@main_bp.route("/switch-club")
def switch_club():
    session.pop('club_id', None)
    session.pop('starting_11', None)
    session.pop('bench', None)
    session.pop('formation', None)
    save_game_state('last_club_id', '')
    return redirect(url_for('main.select_team'))

@main_bp.route("/select-club", methods=["GET", "POST"])
def select_team():
    if request.method == "POST":
        club_id = request.form.get("club_id")
        if club_id:
            session['club_id'] = int(club_id)
            session['season'] = '2025/26'
            session.modified = True
            save_game_state('last_club_id', club_id)
            return redirect(url_for('main.dashboard'))
            
    leagues = {}
    clubs = Club.query.all()
    
    # Pre-fetch standings to show current positions
    standings_map = {}
    from models import Standing
    for s in Standing.query.all():
        standings_map[s.club_id] = s
    
    # Calculate league positions for all clubs
    league_positions = {}
    for league in set([c.league for c in clubs]):
        league_clubs = [c for c in clubs if c.league == league]
        league_club_ids = [c.id for c in league_clubs]
        league_standings = Standing.query.filter(Standing.club_id.in_(league_club_ids)).order_by(
            Standing.points.desc(), Standing.gd.desc(), Standing.gf.desc()
        ).all()
        for i, s in enumerate(league_standings):
            league_positions[s.club_id] = i + 1
            
    # Augment clubs with current status data for the UI
    for club in clubs:
        if club.league not in leagues:
            leagues[club.league] = []
        club.current_position = league_positions.get(club.id, "--")
        s = standings_map.get(club.id)
        club.current_points = s.points if s else 0
        leagues[club.league].append(club)
        
    return render_template("selection.html", leagues=leagues)

@main_bp.route("/new-game", methods=["GET", "POST"])
def new_game():
    session.clear()
    db.drop_all()
    db.create_all()
    from data.seed_data import seed_all
    seed_all()
    save_game_state('last_club_id', '')
    save_game_state('last_formation', '')
    save_game_state('last_starting_11', '')
    return redirect(url_for('main.select_team'))

@main_bp.route("/")
def dashboard():
    club_id = session.get('club_id')
    if not club_id:
        try:
            from models.game_state import GameState
            state = GameState.query.filter_by(key='last_club_id').first()
            if state and state.value:
                club_id = int(state.value)
                session['club_id'] = club_id
                session.modified = True
        except:
            pass

    my_club = get_player_club()
    if not my_club:
        return redirect(url_for('main.select_team'))
    
    from models import Fixture, Standing

    # Next unplayed fixture
    next_fixture = Fixture.query.filter(
        ((Fixture.home_club_id == my_club.id) | (Fixture.away_club_id == my_club.id)),
        Fixture.played == False
    ).order_by(Fixture.match_date).first()

    # Get ALL clubs in same league
    league_clubs = Club.query.filter_by(league=my_club.league).all()
    league_club_ids = [c.id for c in league_clubs]
    
    # Get standings for all clubs in this league (Points > GD > GF)
    from models import Standing
    standings = Standing.query.filter(
        Standing.club_id.in_(league_club_ids)
    ).order_by(
        Standing.points.desc(),
        Standing.gd.desc(),
        Standing.gf.desc()
    ).all()
    
    # Find user's position
    league_position = '--'
    for i, s in enumerate(standings):
        if s.club_id == my_club.id:
            league_position = i + 1
            break
            
    # Auto-create standing if missing (should be handled by fixtures too, but safe for dashboard)
    if league_position == '--':
        user_standing = Standing.query.filter_by(club_id=my_club.id).first()
        if not user_standing:
            user_standing = Standing(
                club_id=my_club.id,
                season_id=1, # Default to first season if not exist
                played=0, won=0, drawn=0, lost=0,
                gf=0, ga=0, gd=0, points=0
            )
            db.session.add(user_standing)
            db.session.commit()
            # Re-query
            standings = Standing.query.filter(
                Standing.club_id.in_(league_club_ids)
            ).order_by(Standing.points.desc(), Standing.gd.desc(), Standing.gf.desc()).all()
            for i, s in enumerate(standings):
                if s.club_id == my_club.id:
                    league_position = i + 1
                    break

    # Recent form (last 5 played)
    recent_matches = Fixture.query.filter(
        ((Fixture.home_club_id == my_club.id) | (Fixture.away_club_id == my_club.id)),
        Fixture.played == True
    ).order_by(Fixture.match_date.desc()).limit(5).all()

    form = []
    for m in recent_matches:
        if m.home_club_id == my_club.id:
            if m.home_score > m.away_score: form.append('W')
            elif m.home_score == m.away_score: form.append('D')
            else: form.append('L')
        else:
            if m.away_score > m.home_score: form.append('W')
            elif m.away_score == m.home_score: form.append('D')
            else: form.append('L')

    return render_template("dashboard.html",
        club=my_club,
        next_fixture=next_fixture,
        league_position=league_position,
        recent_form=form
    )

@main_bp.route("/squad")
def squad():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
        
    players = Player.query.filter_by(club_id=my_club.id).order_by(Player.overall.desc()).all()
    return render_template("squad.html", club=my_club, players=players)

@main_bp.route("/league")
def league():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
        
    # Get current season
    season = Season.query.filter_by(league=my_club.league, year=2025).first()
    
    if season:
        standings = Standing.query.filter_by(season_id=season.id)\
            .order_by(Standing.points.desc(), Standing.gd.desc(), Standing.gf.desc()).all()
    else:
        # Fallback if season object not found
        league_club_ids = [c.id for c in Club.query.filter_by(league=my_club.league).all()]
        standings = Standing.query.filter(Standing.club_id.in_(league_club_ids))\
            .order_by(Standing.points.desc(), Standing.gd.desc(), Standing.gf.desc()).all()
        
    return render_template("league.html", league_name=my_club.league, standings=standings, my_club_id=my_club.id)

match_states = {}

@main_bp.route("/match/<int:match_id>/lineup", methods=["GET", "POST"])
def match_lineup(match_id):
    from models import Fixture
    match = Fixture.query.get_or_404(match_id)
    user_club_id = session.get('club_id')
    if not user_club_id:
        return redirect(url_for('main.select_team'))

    if request.method == "POST":
        data = request.json
        session['starting_11'] = data.get('starting_11', [])
        session['bench'] = data.get('bench', [])
        session['formation'] = data.get('formation', '4-3-3')
        session['home_kit_color'] = data.get('home_kit_color', '#0066CC')
        session['away_kit_color'] = data.get('away_kit_color', '#CC0000')
        session.modified = True
        
        import json
        save_game_state('last_formation', data.get('formation', '4-3-3'))
        save_game_state('last_starting_11', json.dumps(data.get('starting_11', [])))
        
        return jsonify({'redirect': url_for('main.play_match', match_id=match_id)})

    all_players = Player.query.filter_by(club_id=user_club_id).all()
    # Group by position for display
    players_by_position = {
        'GK': [p for p in all_players if p.position == 'GK'],
        'DEF': [p for p in all_players if p.position in ['RB', 'CB', 'LB']],
        'MID': [p for p in all_players if p.position in ['CDM', 'CM', 'CAM']],
        'ATT': [p for p in all_players if p.position in ['LW', 'RW', 'ST']]
    }
    
    # Prepare player data for JSON/JS
    players_json = []
    for p in all_players:
        players_json.append({
            'id': p.id,
            'name': p.name,
            'position': p.position,
            'overall': p.overall
        })

    return render_template('lineup.html', 
                         match=match, 
                         players_by_position=players_by_position,
                         all_players=players_json)

import json
@main_bp.route('/tactics/save', methods=['POST'])
def save_tactics():
    try:
        import json
        data = request.json
        club_id = session.get('club_id')
        if not club_id:
            return jsonify({'error': 'No club selected'}), 400
        
        starting_ids = [
            s['player_id'] for s in data.get('starting_xi', []) 
            if s.get('player_id')
        ]
        all_players = Player.query.filter_by(
            club_id=club_id).all()
        bench_ids = [
            p.id for p in all_players 
            if p.id not in starting_ids
        ]
        
        session['starting_11'] = starting_ids
        session['bench'] = bench_ids
        session['formation'] = data.get('formation', '4-3-3')
        session['mentality'] = data.get('mentality', 'Balanced')
        session.modified = True
        
        save_game_state('last_formation', data.get('formation', '4-3-3'))
        import json
        save_game_state('last_starting_11', json.dumps(starting_ids))
        
        from models.tactics import TacticsSetup
        tactics = TacticsSetup.query.filter_by(
            club_id=club_id).first()
        if not tactics:
            tactics = TacticsSetup(club_id=club_id)
            db.session.add(tactics)
        
        tactics.formation = data.get('formation', '4-3-3')
        tactics.mentality = data.get('mentality', 'Balanced')
        tactics.pressing = data.get('pressing', 'Medium')
        tactics.starting_xi_ids = json.dumps(starting_ids)
        db.session.commit()
        
        return jsonify({
            'status': 'saved', 
            'message': 'Tactics saved successfully!'
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@main_bp.route('/tactics')
def tactics():
    try:
        club_id = session.get('club_id')
        if not club_id:
            return redirect('/')
        
        club = Club.query.get(club_id)
        if not club:
            return redirect('/')
        
        all_players = Player.query.filter_by(
            club_id=club_id
        ).order_by(Player.overall.desc()).all()
        
        # Safely load saved tactics
        saved_xi_ids = []
        saved_formation = '4-3-3'
        saved_mentality = 'Balanced'
        saved_pressing = 'Medium'
        
        try:
            from models.tactics import TacticsSetup
            saved = TacticsSetup.query.filter_by(
                club_id=club_id).first()
            if saved:
                saved_formation = saved.formation or '4-3-3'
                saved_mentality = saved.mentality or 'Balanced'
                saved_pressing = saved.pressing or 'Medium'
                if saved.starting_xi_ids:
                    import json
                    saved_xi_ids = json.loads(
                        saved.starting_xi_ids)
        except Exception as e:
            print(f"Tactics load error: {e}")
            saved_xi_ids = []
        
        return render_template('tactics.html',
            club=club,
            all_players=all_players,
            saved_xi_ids=saved_xi_ids,
            saved_formation=saved_formation,
            saved_mentality=saved_mentality,
            saved_pressing=saved_pressing
        )
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"<pre>Tactics error: {traceback.format_exc()}</pre>", 500
@main_bp.route("/match/<int:match_id>")
def play_match(match_id):
    try:
        from models import Fixture
        match = Fixture.query.get_or_404(match_id)
        user_club_id = session.get('club_id')
        
        starting_11 = []
        bench = []
        
        # Try to load from session first
        starting_ids = session.get('starting_11')
        bench_ids = session.get('bench')
        
        if starting_ids and bench_ids:
            # Maintain order from starting_ids for lineup display if needed
            all_starting = Player.query.filter(Player.id.in_(starting_ids)).all()
            starting_map = {p.id: p for p in all_starting}
            starting_11 = [starting_map[pid] for pid in starting_ids if pid in starting_map]
            
            all_bench = Player.query.filter(Player.id.in_(bench_ids)).all()
            bench_map = {p.id: p for p in all_bench}
            bench = [bench_map[pid] for pid in bench_ids if pid in bench_map]
        
        if not starting_11 and user_club_id:
            # Fallback auto-selection
            all_players = Player.query.filter_by(club_id=user_club_id).all()
            position_order = ['GK','RB','CB','LB','CDM','CM','CAM','LW','RW','ST']
            sorted_players = sorted(all_players, key=lambda p: position_order.index(p.position) if p.position in position_order else 99)
            starting_11 = sorted_players[:11]
            bench = sorted_players[11:]
            
        formation = session.get('formation', '4-3-3')
            
        return render_template('match_day.html', match=match, starting_11=starting_11, bench=bench, formation=formation)
    except Exception as e:
        import traceback
        return f"<pre>{traceback.format_exc()}</pre>", 500

@main_bp.route("/match/<int:match_id>/start", methods=["POST"])
def start_match(match_id):
    try:
        from models import Fixture
        match = Fixture.query.get_or_404(match_id)
        
        from engine.match_engine import simulate_match    
        events = simulate_match(match)
        
        match_states[match_id] = {
            'events': events,
            'started_at': time.time(),
            'home_score': 0,
            'away_score': 0
        }
        return jsonify({"status": "started"})
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'traceback': traceback.format_exc()}), 500

@main_bp.route("/match/<int:match_id>/poll")
def poll_match(match_id):
    try:
        if match_id not in match_states:
            return jsonify({'error': 'Match not started', 'minute': 0, 'events': [], 'finished': False})
            
        state = match_states[match_id]
        # Return ALL events, frontend filters by displayMinute
        return jsonify({
            "minute": int((time.time() - state['started_at']) / 1.5),
            "events": state['events'],
            "finished": False
        })
    except Exception as e:
        import traceback
        return jsonify({'error': str(e)}), 500

@main_bp.route("/match/<int:match_id>/substitution", methods=["POST"])
def make_substitution(match_id):
    try:
        data = request.json
        subs = data.get('substitutions', [])
        # Store in session so they persist across requests if needed
        key = f'subs_{match_id}'
        existing = session.get(key, [])
        existing.extend(subs)
        session[key] = existing
        return jsonify({'status': 'ok', 'subs_recorded': len(subs)})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@main_bp.route("/transfers")
def transfers():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
    return render_template("transfers.html", club=my_club)

@main_bp.route("/api/transfer/search")
def transfer_search():
    my_club = get_player_club()
    query = request.args.get('q', '')
    pos = request.args.get('pos', '')
    
    players = Player.query.filter(Player.club_id != my_club.id)
    if query:
        players = players.filter(Player.name.ilike(f"%{query}%"))
    if pos:
        players = players.filter(Player.position == pos)
        
    players = players.order_by(Player.overall.desc()).limit(20).all()
    
    results = []
    for p in players:
        # Base realistic value proxy
        val = (p.overall ** 3) * 100
        results.append({
            "id": p.id, "name": p.name, "overall": p.overall, "position": p.position,
            "age": p.age, "value": val, "club": p.club.name, "wage": p.wage_per_week
        })
    return jsonify(results)

@main_bp.route("/api/transfer/bid", methods=["POST"])
def transfer_bid():
    my_club = get_player_club()
    data = request.json
    player_id = data.get('player_id')
    offer_amount = float(data.get('amount', 0))
    
    player = Player.query.get(player_id)
    if not player:
        return jsonify({"result": "error", "message": "Player not found"}), 404
        
    if offer_amount > my_club.transfer_budget:
        return jsonify({"result": "rejected", "message": "Board blocked: Insufficient transfer funds."})
    
    market_value = (player.overall ** 3) * 100
    
    if offer_amount >= market_value * 0.95:
        # ACCEPT - move player to user club
        old_club_name = player.club.name
        player.club_id = my_club.id
        # Deduct budget
        my_club.transfer_budget -= offer_amount
        db.session.commit()
        return jsonify({
            'result': 'accepted',
            'message': f'{old_club_name} accepts your offer of €{offer_amount:,.0f}! {player.name} joins your club!',
            'new_budget': my_club.transfer_budget
        })
    elif offer_amount >= market_value * 0.75:
        # COUNTER
        counter = int(market_value * 0.97)
        return jsonify({
            'result': 'counter',
            'counter_amount': counter,
            'message': f'{player.club.name} rejects but counters with €{counter:,.0f}.'
        })
    else:
        # REJECT
        return jsonify({
            'result': 'rejected',
            'message': f'{player.club.name} rejects your offer. Try a higher bid.'
        })

@main_bp.route('/match/<int:match_id>/finish', methods=['POST'])
def finish_match(match_id):
    try:
        data = request.json
        from models import Fixture
        match = Fixture.query.get(match_id)
        if not match:
            return jsonify({'status': 'error', 'message': 'Match not found'}), 404

        if not match.played:
            match.home_score = data['score_home']
            match.away_score = data['score_away']
            match.played = True
            db.session.commit()
            update_standings(match)

            # Auto-simulate all other unplayed fixtures on the same date
            same_day_fixtures = Fixture.query.filter_by(
                match_date=match.match_date,
                played=False
            ).all()

            for fixture in same_day_fixtures:
                if fixture.id == match_id:
                    continue
                home_club = Club.query.get(fixture.home_club_id)
                away_club = Club.query.get(fixture.away_club_id)
                h = home_club.overall_rating if home_club else 75
                a = away_club.overall_rating if away_club else 75
                hg = max(0, min(7, int(random.gauss(h / 25, 1.2))))
                ag = max(0, min(7, int(random.gauss(a / 25, 1.2))))
                fixture.home_score = hg
                fixture.away_score = ag
                fixture.played = True
                db.session.commit()
                update_standings(fixture)

            # Update board confidence for the user's club
            user_club_id = session.get('club_id')
            if user_club_id:
                # Find the result for the user's club in THIS specific match
                result = None
                if match.home_club_id == user_club_id:
                    if match.home_score > match.away_score: result = 'W'
                    elif match.home_score == match.away_score: result = 'D'
                    else: result = 'L'
                elif match.away_club_id == user_club_id:
                    if match.away_score > match.home_score: result = 'W'
                    elif match.away_score == match.home_score: result = 'D'
                    else: result = 'L'
                
                if result:
                    # Get updated position
                    current_club = Club.query.get(user_club_id)
                    league_clubs = Club.query.filter_by(league=current_club.league).all()
                    total_clubs = len(league_clubs)
                    all_standings = Standing.query.filter(
                        Standing.club_id.in_([c.id for c in league_clubs])
                    ).order_by(Standing.points.desc(), Standing.gd.desc(), Standing.gf.desc()).all()
                    
                    position = next((i+1 for i, s in enumerate(all_standings) 
                                   if s.club_id == user_club_id), total_clubs)
                    
                    update_board_confidence(user_club_id, result, position, total_clubs)

        return jsonify({'status': 'saved'})
    except Exception as e:
        import traceback
        return jsonify({'status': 'error', 'message': str(e), 'traceback': traceback.format_exc()}), 500


def update_standings(match):
    from models import Standing
    
    # Get or create home standing
    home_s = Standing.query.filter_by(
        season_id=match.season_id,
        club_id=match.home_club_id
    ).first()
    if not home_s:
        home_s = Standing(
            season_id=match.season_id,
            club_id=match.home_club_id,
            played=0, won=0, drawn=0, lost=0,
            gf=0, ga=0, gd=0, points=0
        )
        db.session.add(home_s)
        db.session.flush()
    
    # Get or create away standing
    away_s = Standing.query.filter_by(
        season_id=match.season_id,
        club_id=match.away_club_id
    ).first()
    if not away_s:
        away_s = Standing(
            season_id=match.season_id,
            club_id=match.away_club_id,
            played=0, won=0, drawn=0, lost=0,
            gf=0, ga=0, gd=0, points=0
        )
        db.session.add(away_s)
        db.session.flush()
    
    # Update stats
    home_s.played += 1
    away_s.played += 1
    home_s.gf += match.home_score
    home_s.ga += match.away_score
    away_s.gf += match.away_score
    away_s.ga += match.home_score
    home_s.gd = home_s.gf - home_s.ga
    away_s.gd = away_s.gf - away_s.ga
    
    if match.home_score > match.away_score:
        home_s.won += 1
        home_s.points += 3
        away_s.lost += 1
    elif match.home_score == match.away_score:
        home_s.drawn += 1
        home_s.points += 1
        away_s.drawn += 1
        away_s.points += 1
    else:
        away_s.won += 1
        away_s.points += 3
        home_s.lost += 1
    
    try:
        db.session.commit()
        print(f"Standings updated: {match.home_club.name} {match.home_score} - {match.away_score} {match.away_club.name}")
    except Exception as e:
        db.session.rollback()
        print(f"Error updating standings: {e}")

def update_board_confidence(club_id, match_result, league_position, total_clubs):
    club = Club.query.get(club_id)
    if not club: return
    
    current = club.board_confidence or 50
    
    # Match result impact
    if match_result == 'W': current += 5
    elif match_result == 'D': current += 1
    elif match_result == 'L': current -= 7
    
    # League position impact
    position_ratio = league_position / total_clubs
    if position_ratio <= 0.2: current += 3       # Top 20%
    elif position_ratio <= 0.4: current += 1     # Top 40%
    elif position_ratio >= 0.8: current -= 5     # Bottom 20%
    elif position_ratio >= 0.6: current -= 2     # Bottom 40%
    
    club.board_confidence = max(0, min(100, current))
    db.session.commit()
    
    # Board messages
    if club.board_confidence <= 20:
        add_inbox_message(club_id, "Board Performance Review", "The board is extremely concerned about recent results. Immediate improvement is required. Based on current league standing and result quality, your confidence rating has been updated accordingly. We urge you to focus on consistency and ensure the team's playing style reflects the standards expected at this club.")
    elif club.board_confidence <= 40:
        add_inbox_message(club_id, "Board Performance Review", "Results have been disappointing. The board expects better performances. Based on current league standing and result quality, your confidence rating has been updated accordingly. We urge you to focus on consistency and ensure the team's playing style reflects the standards expected at this club.")
    elif club.board_confidence >= 80:
        add_inbox_message(club_id, "Board Performance Review", "Excellent work! The board is very pleased with recent performances. Based on current league standing and result quality, your confidence rating has been updated accordingly. We urge you to focus on consistency and ensure the team's playing style reflects the standards expected at this club.")
    elif club.board_confidence >= 65:
        add_inbox_message(club_id, "Board Performance Review", "Good results recently. Keep up the positive momentum. Based on current league standing and result quality, your confidence rating has been updated accordingly. We urge you to focus on consistency and ensure the team's playing style reflects the standards expected at this club.")

def add_inbox_message(club_id, subject_text, message_text):
    from models.inbox import InboxMessage
    msg = InboxMessage(
        club_id=club_id,
        subject=subject_text,
        message=message_text,
        is_read=False
    )
    db.session.add(msg)
    db.session.commit()

@main_bp.route('/admin/fix-nationalities')
def fix_nationalities():
    players = Player.query.filter(
        (Player.nationality == 'Unknown') | 
        (Player.nationality == None) |
        (Player.nationality == '')
    ).all()
    
    fixed = 0
    from data.seed_data import get_nationality
    for player in players:
        club = Club.query.get(player.club_id)
        if club:
            player.nationality = get_nationality(club.league)
            fixed += 1
    
    db.session.commit()
    return jsonify({'fixed': fixed, 'message': f'Fixed {fixed} players'})


@main_bp.route("/finances")
def finances():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
        
    players = Player.query.filter_by(club_id=my_club.id).all()
    weekly_wages = sum((p.wage_per_week or 0) for p in players)
    
    return render_template("finances.html", club=my_club, weekly_wages=weekly_wages)

@main_bp.route("/fixtures")
def fixtures():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
        
    from models import Fixture, Season
    import random
    from datetime import date, timedelta
    
    # Check if a season exists for this league, if not create one and generate fixtures
    season = Season.query.filter_by(league=my_club.league, year=2025).first()
    if not season:
        season = Season(year=2025, league=my_club.league)
        db.session.add(season)
        db.session.flush()
        
        # Auto-generate fixtures (round-robin)
        league_clubs = Club.query.filter_by(league=my_club.league).all()
        club_ids = [c.id for c in league_clubs]
        
        if len(club_ids) % 2 != 0:
            club_ids.append(None) # Bye week pseudo-club
            
        n = len(club_ids)
        match_date = date(2025, 8, 15) # Example start date
        
        # First half
        for round in range(n - 1):
            for i in range(n // 2):
                home = club_ids[i]
                away = club_ids[n - 1 - i]
                if home is not None and away is not None:
                    fixture = Fixture(season_id=season.id, home_club_id=home, away_club_id=away, match_date=match_date)
                    db.session.add(fixture)
            
            club_ids.insert(1, club_ids.pop())
            match_date += timedelta(days=7)
            
        # Second half (reverse home/away)
        for round in range(n - 1):
            for i in range(n // 2):
                home = club_ids[i]
                away = club_ids[n - 1 - i]
                if home is not None and away is not None:
                    fixture = Fixture(season_id=season.id, home_club_id=away, away_club_id=home, match_date=match_date)
                    db.session.add(fixture)
            
            club_ids.insert(1, club_ids.pop())
            match_date += timedelta(days=7)
            
        db.session.commit()
        
    # Get fixtures for my club
    club_fixtures = Fixture.query.filter(
        (Fixture.home_club_id == my_club.id) | (Fixture.away_club_id == my_club.id)
    ).order_by(Fixture.match_date).all()
    
    return render_template("fixtures.html", club=my_club, fixtures=club_fixtures)

@main_bp.route("/inbox")
def inbox():
    my_club = get_player_club()
    if not my_club:
        return abort(404)
        
    from models import InboxMessage as Message
    messages = Message.query.filter_by(club_id=my_club.id).order_by(Message.date_sent.desc(), Message.id.desc()).all()
    
    # Auto-seed if empty
    if not messages:
        msg1 = Message(club_id=my_club.id, subject="Welcome to the Club", message="Welcome, Manager. The board has full confidence in your ability to lead this club forward. Our ambition this season is clear - we expect you to deliver results that match our standing in this league. Your transfer budget has been allocated and the squad is yours to shape. We look forward to seeing your vision unfold on the pitch.")
        msg2 = Message(club_id=my_club.id, subject="Transfer Window Open", message="The transfer window is now officially open. You have been allocated a transfer budget to strengthen the squad as you see fit. The board trusts your judgment on recruitment - however, we expect any significant expenditure to be matched by improved performances. Wage budget constraints must also be respected. Good luck in the market.")
        msg3 = Message(club_id=my_club.id, subject="Board Performance Review", message="The board has reviewed recent match performances and results. Based on current league standing and result quality, your confidence rating has been updated accordingly. We urge you to focus on consistency and ensure the team's playing style reflects the standards expected at this club.")
        
        db.session.add_all([msg1, msg2, msg3])
        db.session.commit()
        
        messages = Message.query.filter_by(club_id=my_club.id).order_by(Message.date_sent.desc(), Message.id.desc()).all()
        
    return render_template("inbox.html", club=my_club, messages=messages)

@main_bp.route("/api/inbox/read/<int:msg_id>", methods=["POST"])
def read_message(msg_id):
    my_club = get_player_club()
    if not my_club:
        return jsonify({"status": "error"}), 403
        
    from models import InboxMessage as Message
    msg = Message.query.filter_by(id=msg_id, club_id=my_club.id).first()
    if msg:
        msg.is_read = True
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "not found"}), 404
