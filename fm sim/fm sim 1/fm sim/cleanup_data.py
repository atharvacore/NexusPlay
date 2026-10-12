import json
import os

# 1. Global Cleanup of "mixed names" in all JSON files
data_dir = r"d:\RAIT SEM 1\fm sim\data"
json_files = ["premier_league.json", "la_liga.json", "bundesliga.json", "serie_a.json", "ligue_1.json"]

# Suffixes that were overused or mixed in incorrectly
fixes = {
    " De Gea": " Garcia",
    " Rice": " Hernandez", # Some Rice's are fine (Declan), but many are messed up
    " Grealish": " Martinez",
    " Saka": " Lopez",
    " Rashford": " Rodriguez",
    " Kane": " Sanchez",
    " Foden": " Perez",
}

for filename in json_files:
    path = os.path.join(data_dir, filename)
    if not os.path.exists(path): continue
    
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    for old, new in fixes.items():
        content = content.replace(old, new)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Global name cleanup done.")

# 2. Re-apply the REAL squads on top of the cleaned files
import patch_players
# (patch_players.py already has the logic to open and save files)

print("Real squads re-applied.")
