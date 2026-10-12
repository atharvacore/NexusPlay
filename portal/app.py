import os
import subprocess
import webbrowser
from threading import Timer
from flask import Flask, render_template, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
GAMES = {
    "battle_sim": {
        "title": "Epic Battle Simulator",
        "desc": "A massive low-poly 3D battle simulator where you can pitch massive armies against each other in real time.",
        "path": r"..\main.py",
        "cwd": r"..",
        "image": "images/battle_sim_thumb_1775208030937.png"
    },
    "fm_sim": {
        "title": "Football Manager Sim",
        "desc": "A football club management simulator. Create your team, manage tactics, and win the league!",
        "path": r"..\fm sim\fm sim 1\fm sim\app.py",
        "cwd": r"..\fm sim\fm sim 1\fm sim",
        "image": "images/fm_sim_thumb_1775208048832.png"
    },
    "minecraft_ai": {
        "title": "Minecraft AI Builder",
        "desc": "A voxel sandbox game with an AI companion that builds structures for you over chat.",
        "path": r"..\minecarft_ai_project (2)\minecarft_ai_project\main.py",
        "cwd": r"..\minecarft_ai_project (2)\minecarft_ai_project",
        "image": "images/minecraft_ai_thumb_1775208066174.png"
    }
}

running_processes = {}

@app.route('/')
def index():
    return render_template('index.html', games=GAMES)

@app.route('/api/launch/<game_id>', methods=['POST'])
def launch_game(game_id):
    if game_id not in GAMES:
        return jsonify({"error": "Game not found"}), 404
        
    game = GAMES[game_id]
    
    try:
        # Check if already running 
        if game_id in running_processes:
            process = running_processes[game_id]
            if process.poll() is None:
                return jsonify({"status": "already_running"})

        # Get absolute paths to avoid issues
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if game_id == "battle_sim":
            cwd = base_dir
            script = os.path.join(base_dir, "main.py")
        elif game_id == "fm_sim":
            cwd = os.path.join(base_dir, "fm sim", "fm sim 1", "fm sim")
            script = os.path.join(cwd, "app.py")
        else:
            cwd = os.path.join(base_dir, "minecarft_ai_project (2)", "minecarft_ai_project")
            script = os.path.join(cwd, "main.py")

        print(f"Launching {game['title']} - Cwd: {cwd}, Script: {script}")

        env = os.environ.copy()
        env['LAUNCHED_FROM_PORTAL'] = '1'

        proc = subprocess.Popen(
            ["python", script],
            cwd=cwd,
            env=env,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        running_processes[game_id] = proc
        
        return jsonify({"status": "success", "message": f"Successfully launched {game['title']}"})
    except Exception as e:
        print(f"Error launching game: {e}")
        return jsonify({"error": str(e)}), 500

def open_browser():
    webbrowser.open("http://127.0.0.1:8000/")

if __name__ == '__main__':
    Timer(1.0, open_browser).start()
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
