import json
import os

def patch_json(filename, club_patches):
    path = os.path.join(r"d:\RAIT SEM 1\fm sim\data", filename)
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for club in data['clubs']:
        if club['name'] in club_patches:
            club['players'] = club_patches[club['name']]
    
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Sample REAL 2025/26 Arsenals (Simplified for the task)
arsenal_players = [
    {"name": "David Raya", "nationality": "Spain", "age": 30, "position": "GK", "overall": 84, "potential": 86, "wage_per_week": 120000},
    {"name": "Neto", "nationality": "Brazil", "age": 36, "position": "GK", "overall": 78, "potential": 78, "wage_per_week": 80000},
    {"name": "William Saliba", "nationality": "France", "age": 24, "position": "CB", "overall": 88, "potential": 92, "wage_per_week": 180000},
    {"name": "Gabriel Magalhães", "nationality": "Brazil", "age": 27, "position": "CB", "overall": 86, "potential": 88, "wage_per_week": 150000},
    {"name": "Jurrien Timber", "nationality": "Netherlands", "age": 24, "position": "CB", "overall": 82, "potential": 88, "wage_per_week": 120000},
    {"name": "Ben White", "nationality": "England", "age": 27, "position": "RB", "overall": 84, "potential": 86, "wage_per_week": 140000},
    {"name": "Riccardo Calafiori", "nationality": "Italy", "age": 23, "position": "LB", "overall": 83, "potential": 89, "wage_per_week": 110000},
    {"name": "Oleksandr Zinchenko", "nationality": "Ukraine", "age": 28, "position": "LB", "overall": 80, "potential": 80, "wage_per_week": 100000},
    {"name": "Declan Rice", "nationality": "England", "age": 26, "position": "CDM", "overall": 87, "potential": 91, "wage_per_week": 240000},
    {"name": "Thomas Partey", "nationality": "Ghana", "age": 32, "position": "CDM", "overall": 83, "potential": 83, "wage_per_week": 200000},
    {"name": "Martin Ødegaard", "nationality": "Norway", "age": 26, "position": "CAM", "overall": 89, "potential": 91, "wage_per_week": 240000},
    {"name": "Mikel Merino", "nationality": "Spain", "age": 29, "position": "CM", "overall": 84, "potential": 84, "wage_per_week": 130000},
    {"name": "Bukayo Saka", "nationality": "England", "age": 23, "position": "RW", "overall": 88, "potential": 92, "wage_per_week": 280000},
    {"name": "Gabriel Martinelli", "nationality": "Brazil", "age": 24, "position": "LW", "overall": 84, "potential": 89, "wage_per_week": 160000},
    {"name": "Leandro Trossard", "nationality": "Belgium", "age": 30, "position": "LW", "overall": 82, "potential": 82, "wage_per_week": 100000},
    {"name": "Kai Havertz", "nationality": "Germany", "age": 26, "position": "ST", "overall": 85, "potential": 88, "wage_per_week": 200000},
    {"name": "Gabriel Jesus", "nationality": "Brazil", "age": 28, "position": "ST", "overall": 82, "potential": 83, "wage_per_week": 200000},
]

man_city_players = [
    {"name": "Ederson", "nationality": "Brazil", "age": 32, "position": "GK", "overall": 88, "potential": 88, "wage_per_week": 200000},
    {"name": "Stefan Ortega", "nationality": "Germany", "age": 32, "position": "GK", "overall": 80, "potential": 80, "wage_per_week": 90000},
    {"name": "Ruben Dias", "nationality": "Portugal", "age": 28, "position": "CB", "overall": 89, "potential": 91, "wage_per_week": 250000},
    {"name": "John Stones", "nationality": "England", "age": 31, "position": "CB", "overall": 87, "potential": 87, "wage_per_week": 250000},
    {"name": "Manuel Akanji", "nationality": "Switzerland", "age": 30, "position": "CB", "overall": 84, "potential": 85, "wage_per_week": 180000},
    {"name": "Nathan Aké", "nationality": "Netherlands", "age": 30, "position": "CB", "overall": 84, "potential": 84, "wage_per_week": 160000},
    {"name": "Kyle Walker", "nationality": "England", "age": 35, "position": "RB", "overall": 84, "potential": 84, "wage_per_week": 175000},
    {"name": "Josko Gvardiol", "nationality": "Croatia", "age": 23, "position": "LB", "overall": 85, "potential": 91, "wage_per_week": 200000},
    {"name": "Rodri", "nationality": "Spain", "age": 29, "position": "CDM", "overall": 91, "potential": 91, "wage_per_week": 300000},
    {"name": "Mateo Kovacic", "nationality": "Croatia", "age": 31, "position": "CM", "overall": 83, "potential": 83, "wage_per_week": 150000},
    {"name": "Kevin De Bruyne", "nationality": "Belgium", "age": 34, "position": "CM", "overall": 90, "potential": 90, "wage_per_week": 400000},
    {"name": "Bernardo Silva", "nationality": "Portugal", "age": 31, "position": "CM", "overall": 88, "potential": 88, "wage_per_week": 300000},
    {"name": "Phil Foden", "nationality": "England", "age": 25, "position": "CAM", "overall": 89, "potential": 92, "wage_per_week": 225000},
    {"name": "Jack Grealish", "nationality": "England", "age": 30, "position": "LW", "overall": 83, "potential": 83, "wage_per_week": 300000},
    {"name": "Jeremy Doku", "nationality": "Belgium", "age": 23, "position": "LW", "overall": 82, "potential": 89, "wage_per_week": 100000},
    {"name": "Savinho", "nationality": "Brazil", "age": 21, "position": "RW", "overall": 82, "potential": 90, "wage_per_week": 80000},
    {"name": "Erling Haaland", "nationality": "Norway", "age": 25, "position": "ST", "overall": 91, "potential": 94, "wage_per_week": 375000},
]

liverpool_players = [
    {"name": "Alisson Becker", "nationality": "Brazil", "age": 32, "position": "GK", "overall": 89},
    {"name": "Caoimhin Kelleher", "nationality": "Ireland", "age": 26, "position": "GK", "overall": 80},
    {"name": "Virgil van Dijk", "nationality": "Netherlands", "age": 34, "position": "CB", "overall": 89},
    {"name": "Ibrahima Konaté", "nationality": "France", "age": 26, "position": "CB", "overall": 85},
    {"name": "Trent Alexander-Arnold", "nationality": "England", "age": 26, "position": "RB", "overall": 86},
    {"name": "Andrew Robertson", "nationality": "Scotland", "age": 31, "position": "LB", "overall": 84},
    {"name": "Alexis Mac Allister", "nationality": "Argentina", "age": 26, "position": "CM", "overall": 86},
    {"name": "Dominik Szoboszlai", "nationality": "Hungary", "age": 24, "position": "CM", "overall": 84},
    {"name": "Ryan Gravenberch", "nationality": "Netherlands", "age": 23, "position": "CDM", "overall": 82},
    {"name": "Mohamed Salah", "nationality": "Egypt", "age": 33, "position": "RW", "overall": 89},
    {"name": "Luis Díaz", "nationality": "Colombia", "age": 28, "position": "LW", "overall": 84},
    {"name": "Darwin Núñez", "nationality": "Uruguay", "age": 26, "position": "ST", "overall": 82},
    {"name": "Diogo Jota", "nationality": "Portugal", "age": 28, "position": "ST", "overall": 85},
]

real_madrid_players = [
    {"name": "Thibaut Courtois", "nationality": "Belgium", "age": 33, "position": "GK", "overall": 90},
    {"name": "Andriy Lunin", "nationality": "Ukraine", "age": 26, "position": "GK", "overall": 82},
    {"name": "Antonio Rüdiger", "nationality": "Germany", "age": 32, "position": "CB", "overall": 87},
    {"name": "Éder Militão", "nationality": "Brazil", "age": 27, "position": "CB", "overall": 86},
    {"name": "David Alaba", "nationality": "Austria", "age": 33, "position": "CB", "overall": 85},
    {"name": "Daniel Carvajal", "nationality": "Spain", "age": 33, "position": "RB", "overall": 84},
    {"name": "Ferland Mendy", "nationality": "France", "age": 30, "position": "LB", "overall": 82},
    {"name": "Aurélien Tchouaméni", "nationality": "France", "age": 25, "position": "CDM", "overall": 86},
    {"name": "Eduardo Camavinga", "nationality": "France", "age": 22, "position": "CM", "overall": 85},
    {"name": "Federico Valverde", "nationality": "Uruguay", "age": 27, "position": "CM", "overall": 88},
    {"name": "Jude Bellingham", "nationality": "England", "age": 22, "position": "CAM", "overall": 90},
    {"name": "Vinícius Júnior", "nationality": "Brazil", "age": 25, "position": "LW", "overall": 91},
    {"name": "Kylian Mbappé", "nationality": "France", "age": 26, "position": "ST", "overall": 92},
    {"name": "Rodrygo", "nationality": "Brazil", "age": 24, "position": "RW", "overall": 86},
    {"name": "Endrick", "nationality": "Brazil", "age": 19, "position": "ST", "overall": 80, "potential": 93},
]

barcelona_players = [
    {"name": "Marc-André ter Stegen", "nationality": "Germany", "age": 33, "position": "GK", "overall": 89},
    {"name": "Pau Cubarsí", "nationality": "Spain", "age": 18, "position": "CB", "overall": 78, "potential": 90},
    {"name": "Ronald Araújo", "nationality": "Uruguay", "age": 26, "position": "CB", "overall": 86},
    {"name": "Jules Koundé", "nationality": "France", "age": 26, "position": "RB", "overall": 85},
    {"name": "Alejandro Balde", "nationality": "Spain", "age": 21, "position": "LB", "overall": 82},
    {"name": "Pedri", "nationality": "Spain", "age": 22, "position": "CM", "overall": 86},
    {"name": "Gavi", "nationality": "Spain", "age": 21, "position": "CM", "overall": 84},
    {"name": "Frenkie de Jong", "nationality": "Netherlands", "age": 28, "position": "CM", "overall": 87},
    {"name": "Dani Olmo", "nationality": "Spain", "age": 27, "position": "CAM", "overall": 86},
    {"name": "Lamine Yamal", "nationality": "Spain", "age": 18, "position": "RW", "overall": 84, "potential": 94},
    {"name": "Raphinha", "nationality": "Brazil", "age": 28, "position": "LW", "overall": 84},
    {"name": "Robert Lewandowski", "nationality": "Poland", "age": 37, "position": "ST", "overall": 88},
]

bayern_players = [
    {"name": "Manuel Neuer", "nationality": "Germany", "age": 39, "position": "GK", "overall": 86},
    {"name": "Dayot Upamecano", "nationality": "France", "age": 26, "position": "CB", "overall": 84},
    {"name": "Kim Min-jae", "nationality": "South Korea", "age": 28, "position": "CB", "overall": 85},
    {"name": "Alphonso Davies", "nationality": "Canada", "age": 24, "position": "LB", "overall": 83},
    {"name": "Joshua Kimmich", "nationality": "Germany", "age": 30, "position": "CDM", "overall": 87},
    {"name": "Jamal Musiala", "nationality": "Germany", "age": 22, "position": "CAM", "overall": 88},
    {"name": "Leroy Sané", "nationality": "Germany", "age": 29, "position": "RW", "overall": 85},
    {"name": "Harry Kane", "nationality": "England", "age": 32, "position": "ST", "overall": 90},
    {"name": "Michael Olise", "nationality": "France", "age": 23, "position": "RW", "overall": 83},
]

inter_players = [
    {"name": "Yann Sommer", "nationality": "Switzerland", "age": 36, "position": "GK", "overall": 85},
    {"name": "Alessandro Bastoni", "nationality": "Italy", "age": 26, "position": "CB", "overall": 86},
    {"name": "Lautaro Martínez", "nationality": "Argentina", "age": 28, "position": "ST", "overall": 89},
    {"name": "Nicolò Barella", "nationality": "Italy", "age": 28, "position": "CM", "overall": 87},
    {"name": "Marcus Thuram", "nationality": "France", "age": 28, "position": "ST", "overall": 84},
]

psg_players = [
    {"name": "Gianluigi Donnarumma", "nationality": "Italy", "age": 26, "position": "GK", "overall": 87},
    {"name": "Marquinhos", "nationality": "Brazil", "age": 31, "position": "CB", "overall": 86},
    {"name": "Warren Zaïre-Emery", "nationality": "France", "age": 19, "position": "CM", "overall": 82, "potential": 90},
    {"name": "Ousmane Dembélé", "nationality": "France", "age": 28, "position": "RW", "overall": 86},
    {"name": "Bradley Barcola", "nationality": "France", "age": 23, "position": "LW", "overall": 82},
]

club_patches_pl = {"Arsenal": arsenal_players, "Manchester City": man_city_players, "Liverpool": liverpool_players}
club_patches_es = {"Real Madrid": real_madrid_players, "FC Barcelona": barcelona_players}
club_patches_de = {"FC Bayern München": bayern_players}
club_patches_it = {"Inter": inter_players}
club_patches_fr = {"Paris Saint-Germain": psg_players}

def complete_stats(players):
    for p in players:
        p.setdefault("pace", p.get("overall", 70))
        p.setdefault("shooting", p.get("overall", 70))
        p.setdefault("passing", p.get("overall", 70))
        p.setdefault("dribbling", p.get("overall", 70))
        p.setdefault("defending", p.get("overall", 70))
        p.setdefault("physical", p.get("overall", 70))
        p.setdefault("potential", p.get("overall") + 2 if "potential" not in p else p["potential"])
        p.setdefault("morale", 85)
        today_year = 2026
        p.setdefault("contract_end_date", f"{today_year + 3}-06-30")
        p.setdefault("wage_per_week", p["overall"] * 2000)
        p.setdefault("release_clause", p["overall"] * 1000000)

for p_list in [arsenal_players, man_city_players, liverpool_players, real_madrid_players, barcelona_players, bayern_players, inter_players, psg_players]:
    complete_stats(p_list)

patch_json("premier_league.json", club_patches_pl)
patch_json("la_liga.json", club_patches_es)
patch_json("bundesliga.json", club_patches_de)
patch_json("serie_a.json", club_patches_it)
patch_json("ligue_1.json", club_patches_fr)

print("All leagues patched with top teams.")
