import random

match_states = {}

def simulate_match(match):
    """
    Generates all 90 minutes of events at once for a match.
    """
    home_club = match.home_club
    away_club = match.away_club
    
    home_players = list(home_club.players) if home_club else []
    away_players = list(away_club.players) if away_club else []
    
    # Calculate actual squad strength from player ratings
    home_strength = sum(p.overall for p in home_players[:11]) / 11 if home_players else 75
    away_strength = sum(p.overall for p in away_players[:11]) / 11 if away_players else 75
    
    # Home advantage bonus
    home_strength += 3
    
    # Normalize to 0-1 scale for attack/defense
    total = home_strength + away_strength
    home_attack_prob = home_strength / total
    away_attack_prob = away_strength / total
    
    events = []
    home_score = 0
    away_score = 0
    
    # Generate events minute by minute
    for minute in range(1, 91):
        # Each minute has chance of event
        # Higher rated team gets more chances
        
        # Home attack chance
        if random.random() < home_attack_prob * 0.18:
            # Shot on target check
            if random.random() < 0.45:
                # Goal check - affected by away defense
                goal_prob = 0.35 + (home_strength - away_strength) / 200
                goal_prob = max(0.15, min(0.55, goal_prob))
                if random.random() < goal_prob:
                    home_score += 1
                    scorer = _get_scorer(home_players, 'home')
                    events.append({
                        'minute': minute,
                        'type': 'goal',
                        'team': 'home',
                        'player': scorer,
                        'description': random.choice([
                            'Brilliant finish!',
                            'Powerful strike!',
                            'Clinical conversion!',
                            'Header from close range!',
                            'Curled into the corner!'
                        ]),
                        'score_home': home_score,
                        'score_away': away_score
                    })
                else:
                    chancer = _get_scorer(home_players, 'home')
                    events.append({
                        'minute': minute,
                        'type': 'chance',
                        'team': 'home',
                        'player': chancer,
                        'description': 'Good chance!',
                        'score_home': home_score,
                        'score_away': away_score
                    })
        
        # Away attack chance (mirror logic)
        if random.random() < away_attack_prob * 0.18:
            if random.random() < 0.45:
                goal_prob = 0.35 + (away_strength - home_strength) / 200
                goal_prob = max(0.15, min(0.55, goal_prob))
                if random.random() < goal_prob:
                    away_score += 1
                    scorer = _get_scorer(away_players, 'away')
                    events.append({
                        'minute': minute,
                        'type': 'goal',
                        'team': 'away',
                        'player': scorer,
                        'description': random.choice([
                            'Brilliant finish!',
                            'Powerful strike!',
                            'Clinical conversion!',
                            'Stunning volley!',
                            'Slotted past the keeper!'
                        ]),
                        'score_home': home_score,
                        'score_away': away_score
                    })
                else:
                    chancer = _get_scorer(away_players, 'away')
                    events.append({
                        'minute': minute,
                        'type': 'chance',
                        'team': 'away',
                        'player': chancer,
                        'description': 'Close chance!',
                        'score_home': home_score,
                        'score_away': away_score
                    })
        
        # Yellow card (random, low probability)
        if random.random() < 0.012:
            team = random.choice(['home', 'away'])
            players = home_players if team == 'home' else away_players
            if players:
                carded = random.choice(players).name
                events.append({
                    'minute': minute,
                    'type': 'yellow_card',
                    'team': team,
                    'player': carded,
                    'score_home': home_score,
                    'score_away': away_score
                })
        
        # Substitutions after 60 mins
        if minute in [63, 70, 77]:
            if random.random() < 0.7:
                team = random.choice(['home', 'away'])
                players = home_players if team == 'home' else away_players
                bench_players = home_players[11:] if team == 'home' else away_players[11:]
                if players and bench_players:
                    events.append({
                        'minute': minute,
                        'type': 'substitution',
                        'team': team,
                        'player_off': random.choice(players[4:11]).name,
                        'player_on': random.choice(bench_players).name,
                        'score_home': home_score,
                        'score_away': away_score
                    })
    
    return events


def _get_scorer(players, team):
    # Weight scorers by position - attackers score more
    weights = []
    for p in players[:11]:
        if p.position in ['ST', 'CF']:
            weights.append(40)
        elif p.position in ['LW', 'RW', 'CAM']:
            weights.append(25)
        elif p.position in ['CM', 'CAM']:
            weights.append(10)
        else:
            weights.append(3)
    
    if not players or not weights:
        return 'Unknown'
    
    total_weight = sum(weights)
    r = random.random() * total_weight
    cumulative = 0
    for i, w in enumerate(weights):
        cumulative += w
        if r <= cumulative:
            return players[i].name if i < len(players) else players[0].name
    return players[0].name
