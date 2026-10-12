import json
import os
import random
from datetime import date, timedelta

from flask import current_app
from models import Club, Player, db, Season, Fixture, Standing

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Mandatory positions: GK x2, RB x2, CB x4, LB x2, CDM x2, CM x3, CAM x1, LW x2, RW x2, ST x3 = 23
MANDATORY_POSITIONS = (['GK']*2 + ['RB']*2 + ['CB']*4 + ['LB']*2 + 
                      ['CDM']*2 + ['CM']*3 + ['CAM']*1 + ['LW']*2 + ['RW']*2 + ['ST']*3)

# Name pools for squad filling
NAMES_BY_COUNTRY = {
    "England": ["Smith", "Jones", "Taylor", "Brown", "Williams", "Wilson", "Johnson", "Davies", "Robinson", "Wright", "Thompson", "Evans", "Walker", "White", "Roberts", "Green", "Hall", "Wood", "Harris", "Clark"],
    "Spain": ["Garcia", "Rodriguez", "Gonzalez", "Fernandez", "Lopez", "Martinez", "Sanchez", "Perez", "Gomez", "Martin", "Jimenez", "Ruiz", "Hernandez", "Diaz", "Moreno", "Muñoz", "Alvarez", "Romero", "Alonso", "Gutierrez"],
    "Italy": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Romano", "Colombo", "Ricci", "Marino", "Greco", "Bruno", "Gallo", "Conti", "De Luca", "Mancini", "Costa", "Giordano", "Rizzo", "Lombardi", "Moretti"],
    "Germany": ["Müller", "Schmidt", "Schneider", "Fischer", "Meyer", "Weber", "Schulz", "Wagner", "Becker", "Hoffmann", "Schäfer", "Koch", "Bauer", "Richter", "Klein", "Wolf", "Schröder", "Neumann", "Schwarz", "Zimmermann"],
    "France": ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Richard", "Durand", "Dubois", "Moreau", "Laurent", "Simon", "Michel", "Lefebvre", "Leroy", "Roux", "David", "Bertrand", "Morel", "Fournier", "Girard"]
}
FIRST_NAMES = ["Oliver", "Jack", "Harry", "Jacob", "Charlie", "Thomas", "George", "Oscar", "James", "William", "Lucas", "Noah", "Leo", "Theo", "Arthur", "Freddie", "Alfie", "Joshua", "Logan"]

NATIONALITY_POOL = [
    'Brazilian', 'French', 'Spanish', 'German', 'Argentine',
    'Portuguese', 'Dutch', 'Belgian', 'Croatian', 'English',
    'Italian', 'Senegalese', 'Moroccan', 'Colombian', 'Norwegian',
    'Danish', 'Swiss', 'Austrian', 'Polish', 'Czech',
    'Serbian', 'Uruguayan', 'Chilean', 'Mexican', 'Japanese',
    'South Korean', 'Cameroonian', 'Ghanaian', 'Algerian', 'Turkish'
]

NATIONALITIES_BY_LEAGUE = {
    'Premier League': [
        'English', 'English', 'English', 'Welsh', 'Scottish',
        'French', 'Spanish', 'Brazilian', 'Argentine', 'German',
        'Portuguese', 'Dutch', 'Belgian', 'Senegalese', 'Egyptian',
        'Norwegian', 'Swiss', 'Irish', 'Croatian', 'Jamaican'
    ],
    'La Liga': [
        'Spanish', 'Spanish', 'Spanish', 'Spanish', 'Brazilian',
        'Argentine', 'French', 'Portuguese', 'Croatian', 'German',
        'Colombian', 'Uruguayan', 'Chilean', 'Moroccan', 'Dutch',
        'Belgian', 'English', 'Senegalese', 'Welsh', 'Venezuelan'
    ],
    'Serie A': [
        'Italian', 'Italian', 'Italian', 'Italian', 'Brazilian',
        'Argentine', 'French', 'Spanish', 'Albanian', 'Dutch',
        'Portuguese', 'Croatian', 'Serbian', 'Bosnian', 'Swiss',
        'Norwegian', 'Uruguayan', 'Colombian', 'Moroccan', 'Turkish'
    ],
    'Bundesliga': [
        'German', 'German', 'German', 'German', 'French',
        'Spanish', 'Brazilian', 'Austrian', 'Swiss', 'Dutch',
        'Polish', 'Czech', 'Croatian', 'Serbian', 'Japanese',
        'South Korean', 'Moroccan', 'Cameroonian', 'Ghanaian', 'Danish'
    ],
    'Ligue 1': [
        'French', 'French', 'French', 'French', 'Moroccan',
        'Algerian', 'Senegalese', 'Cameroonian', 'Ivorian', 'Malian',
        'Brazilian', 'Argentine', 'Spanish', 'Portuguese', 'Croatian',
        'Guinean', 'Congolese', 'Tunisian', 'Gabonese', 'Swiss'
    ]
}

def get_nationality(league=None):
    if league and league in NATIONALITIES_BY_LEAGUE:
        nat = random.choice(NATIONALITIES_BY_LEAGUE[league])
    else:
        nat = random.choice(NATIONALITY_POOL)
    # Safety check - never return empty
    if not nat or nat.strip() == '' or nat == 'Unknown':
        nat = random.choice(NATIONALITY_POOL)
    return nat

REAL_PLAYER_NATIONALITIES = {
    "Kylian Mbappe": "French",
    "Vinicius Jr": "Brazilian", 
    "Jude Bellingham": "English",
    "Kevin De Bruyne": "Belgian",
    "Erling Haaland": "Norwegian",
    "Harry Kane": "English",
    "Son Heung-min": "South Korean",
    "Marc-Andre ter Stegen": "German",
    "Inaki Pena": "Spanish",
    "Ederson": "Brazilian",
    "Alisson Becker": "Brazilian",
    "Ruben Dias": "Portuguese",
    "Eder Militao": "Brazilian",
    "Robert Lewandowski": "Polish",
    "Luka Modric": "Croatian",
    "Karim Benzema": "French",
    "Sadio Mane": "Senegalese",
    "Mohamed Salah": "Egyptian",
    "Virgil van Dijk": "Dutch",
    "Trent Alexander-Arnold": "English",
    "Andrew Robertson": "Scottish",
    "Dominik Szoboszlai": "Hungarian",
    "Darwin Nunez": "Uruguayan",
    "Luis Diaz": "Colombian",
    "Cody Gakpo": "Dutch",
    "Diogo Jota": "Portuguese",
    "Manuel Neuer": "German",
    "Joshua Kimmich": "German",
    "Leroy Sane": "German",
    "Jamal Musiala": "German",
    "Lionel Messi": "Argentine",
    "Neymar Jr": "Brazilian",
    "Cristiano Ronaldo": "Portuguese",
    "Gianluigi Donnarumma": "Italian",
    "Mike Maignan": "French",
    "Rafael Leao": "Portuguese",
    "Theo Hernandez": "French",
    "Romelu Lukaku": "Belgian",
    "Lautaro Martinez": "Argentine",
    "Nicolo Barella": "Italian",
    "Alessandro Bastoni": "Italian",
    "Khvicha Kvaratskhelia": "Georgian",
    "Victor Osimhen": "Nigerian",
    "Antoine Griezmann": "French",
    "Atletico Griezmann": "French",
    "Jan Oblak": "Slovenian",
    "Pedri": "Spanish",
    "Gavi": "Spanish",
    "Ferran Torres": "Spanish",
    "Ansu Fati": "Spanish",
    "Marco Reus": "German",
    "Gregor Kobel": "Swiss",
    "Emre Can": "German",
    "Riyad Mahrez": "Algerian",
    "Bernardo Silva": "Portuguese",
    "Phil Foden": "English",
    "Jack Grealish": "English",
    "Kyle Walker": "English",
    "John Stones": "English",
    "Bukayo Saka": "English",
    "Martin Odegaard": "Norwegian",
    "Declan Rice": "English",
    "Kai Havertz": "German",
    "David Raya": "Spanish",
    "Gabriel Magalhaes": "Brazilian",
    "William Saliba": "French",
    "Ben White": "English"
}

def load_json(filename: str):
    path = os.path.join(BASE_DIR, filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_liverpool_squad():
    return [
        {"name": "Alisson Becker", "pos": "GK", "rating": 89, "nat": "Brazilian"},
        {"name": "Caoimhin Kelleher", "pos": "GK", "rating": 77, "nat": "Irish"},
        {"name": "Trent Alexander-Arnold", "pos": "RB", "rating": 87, "nat": "English"},
        {"name": "Conor Bradley", "pos": "RB", "rating": 78, "nat": "Northern Irish"},
        {"name": "Virgil van Dijk", "pos": "CB", "rating": 89, "nat": "Dutch"},
        {"name": "Ibrahima Konate", "pos": "CB", "rating": 84, "nat": "French"},
        {"name": "Joel Matip", "pos": "CB", "rating": 76, "nat": "Cameroonian"},
        {"name": "Jarell Quansah", "pos": "CB", "rating": 74, "nat": "English"},
        {"name": "Andrew Robertson", "pos": "LB", "rating": 85, "nat": "Scottish"},
        {"name": "Kostas Tsimikas", "pos": "LB", "rating": 76, "nat": "Greek"},
        {"name": "Wataru Endo", "pos": "CDM", "rating": 79, "nat": "Japanese"},
        {"name": "Stefan Bajcetic", "pos": "CDM", "rating": 72, "nat": "Spanish"},
        {"name": "Dominik Szoboszlai", "pos": "CM", "rating": 84, "nat": "Hungarian"},
        {"name": "Curtis Jones", "pos": "CM", "rating": 80, "nat": "English"},
        {"name": "Ryan Gravenberch", "pos": "CM", "rating": 79, "nat": "Dutch"},
        {"name": "Mac Allister", "pos": "CAM", "rating": 85, "nat": "Argentine"},
        {"name": "Luis Diaz", "pos": "LW", "rating": 85, "nat": "Colombian"},
        {"name": "Cody Gakpo", "pos": "LW", "rating": 82, "nat": "Dutch"},
        {"name": "Mohamed Salah", "pos": "RW", "rating": 90, "nat": "Egyptian"},
        {"name": "Harvey Elliott", "pos": "RW", "rating": 78, "nat": "English"},
        {"name": "Darwin Nunez", "pos": "ST", "rating": 84, "nat": "Uruguayan"},
        {"name": "Diogo Jota", "pos": "ST", "rating": 84, "nat": "Portuguese"},
        {"name": "Ben Doak", "pos": "ST", "rating": 72, "nat": "Scottish"},
    ]

def fill_squad(club, country):
    players = Player.query.filter_by(club_id=club.id).all()
    pos_counts = {}
    for p in players:
        pos_counts[p.position] = pos_counts.get(p.position, 0) + 1
    
    needed_pos = []
    template_counts = {}
    for pos in MANDATORY_POSITIONS:
        template_counts[pos] = template_counts.get(pos, 0) + 1
        
    for pos, count in template_counts.items():
        current = pos_counts.get(pos, 0)
        if current < count:
            needed_pos.extend([pos] * (count - current))
            
    name_pool = NAMES_BY_COUNTRY.get(country, NAMES_BY_COUNTRY["England"])
    for pos in needed_pos:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(name_pool)}"
        # Uniqueness check
        while Player.query.filter_by(club_id=club.id, name=name).first():
            name = f"{random.choice(FIRST_NAMES)} {random.choice(name_pool)}"
            
        rating = random.randint(club.overall_rating - 5, club.overall_rating + 2)
        rating = max(60, min(94, rating))
        
        player = Player(
            name=name, nationality=get_nationality(club.league), age=random.randint(18, 33), position=pos,
            overall=rating, potential=rating + random.randint(0, 8), current_ability=rating,
            club_id=club.id, wage_per_week=random.randint(10, 200) * 1000,
            contract_end_date=date(2028, 6, 30)
        )
        db.session.add(player)

def seed_league_from_file(filename: str, default_country: str):
    data = load_json(filename)
    league_name = data["league"]
    country = data.get("country", default_country)

    # 1. Create Season
    season = Season.query.filter_by(league=league_name, year=2025).first()
    if not season:
        season = Season(year=2025, league=league_name)
        db.session.add(season)
        db.session.flush()

    league_clubs = []
    for club_data in data["clubs"]:
        club = Club.query.filter_by(name=club_data["name"]).first()
        if not club:
            club = Club(
                name=club_data["name"], league=league_name, country=country,
                stadium=club_data.get("stadium", f"{club_data['name']} Stadium"),
                stadium_capacity=club_data.get("stadium_capacity", 30000),
                overall_rating=club_data.get("overall_rating", 75), prestige=club_data.get("prestige", 3),
                transfer_budget=club_data.get("transfer_budget", 30_000_000),
                wage_budget=club_data.get("wage_budget", 800_000),
                board_ambition=club_data.get("board_ambition", "midtable"),
                board_confidence=50
            )
            db.session.add(club)
            db.session.flush()
        league_clubs.append(club)

        # 2. Create Standing for this club
        standing = Standing.query.filter_by(season_id=season.id, club_id=club.id).first()
        if not standing:
            standing = Standing(
                season_id=season.id, club_id=club.id,
                played=0, won=0, drawn=0, lost=0,
                gf=0, ga=0, gd=0, points=0
            )
            db.session.add(standing)

        if club.name == "Liverpool":
            Player.query.filter_by(club_id=club.id).delete()
            for p_info in get_liverpool_squad():
                p = Player(
                    name=p_info["name"], position=p_info["pos"], overall=p_info["rating"],
                    nationality=p_info["nat"], age=random.randint(20, 32), club_id=club.id,
                    potential=p_info["rating"] + 2, current_ability=p_info["rating"],
                    wage_per_week=random.randint(80, 250) * 1000,
                    contract_end_date=date(2029, 6, 30)
                )
                db.session.add(p)
        else:
            for p_data in club_data.get("players", []):
                if not Player.query.filter_by(club_id=club.id, name=p_data["name"]).first():
                    # Get correct nationality for real-named players if specified, or use league pool
                    nat = p_data.get("nationality", "").strip()
                    if not nat or nat == "Unknown" or nat == "":
                        nat = get_nationality(league_name)

                    if p_data["name"] in REAL_PLAYER_NATIONALITIES:
                        nat = REAL_PLAYER_NATIONALITIES[p_data["name"]]

                    p = Player(
                        name=p_data["name"], position=p_data.get("position", "CM"),
                        overall=p_data.get("overall", 70), nationality=nat,
                        age=p_data.get("age", 25), club_id=club.id,
                        potential=p_data.get("potential", p_data.get("overall", 70)),
                        current_ability=p_data.get("overall", 70),
                        wage_per_week=p_data.get("wage_per_week", 40000),
                        contract_end_date=date(2028, 6, 30)
                    )
                    db.session.add(p)
            db.session.flush()
            fill_squad(club, country)

    # 3. Generate Fixtures (Round Robin)
    club_ids = [c.id for c in league_clubs]
    if len(club_ids) % 2 != 0: club_ids.append(None)
    n = len(club_ids)
    match_date = date(2025, 8, 16)
    
    # First half
    temp_ids = list(club_ids)
    for r in range(n - 1):
        for i in range(n // 2):
            home_id, away_id = temp_ids[i], temp_ids[n - 1 - i]
            if home_id and away_id:
                if not Fixture.query.filter_by(season_id=season.id, home_club_id=home_id, away_club_id=away_id).first():
                    f = Fixture(season_id=season.id, home_club_id=home_id, away_club_id=away_id, match_date=match_date)
                    db.session.add(f)
        temp_ids.insert(1, temp_ids.pop())
        match_date += timedelta(days=7)
    
    # Second half
    temp_ids = list(club_ids)
    for r in range(n - 1):
        for i in range(n // 2):
            home_id, away_id = temp_ids[i], temp_ids[n - 1 - i]
            if home_id and away_id:
                if not Fixture.query.filter_by(season_id=season.id, home_club_id=away_id, away_club_id=home_id).first():
                    f = Fixture(season_id=season.id, home_club_id=away_id, away_club_id=home_id, match_date=match_date)
                    db.session.add(f)
        temp_ids.insert(1, temp_ids.pop())
        match_date += timedelta(days=7)

    db.session.commit()

def seed_all():
    seed_league_from_file("premier_league.json", "England")
    seed_league_from_file("la_liga.json", "Spain")
    seed_league_from_file("serie_a.json", "Italy")
    seed_league_from_file("bundesliga.json", "Germany")
    seed_league_from_file("ligue_1.json", "France")
    
    print("Validating squads...")
    for club in Club.query.all():
        count = Player.query.filter_by(club_id=club.id).count()
        if count < 20: raise Exception(f"Squad too small: {club.name}")
        gk_count = Player.query.filter_by(club_id=club.id, position='GK').count()
        if gk_count < 2: raise Exception(f"Not enough GKs: {club.name}")
    print("✅ All data seeded and validated: Squads, Seasons, Fixtures, Standings.")

def seed_database_if_empty():
    if not Club.query.first():
        seed_all()

if __name__ == "__main__":
    from app import app
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_all()
