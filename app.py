import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
import yt_dlp
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Autoriser les requêtes CORS de n'importe quelle origine
CORS(app, resources={r"/*": {"origins": "*"}})

# Charger les cookies depuis les variables d'environnement
cookie_data = os.getenv("YOUTUBE_COOKIES")
if cookie_data:
    cookies = json.loads(cookie_data)  # Convertir les cookies de JSON en dictionnaire
else:
    cookies = None
    print("Aucun cookie trouvé dans les variables d'environnement")

@app.route("/")
def home():
    return "Music Downloader Backend is Running"

@app.route("/download", methods=["POST"])
def download_song():
    data = request.json
    song_name = data.get("song_name")

    if not song_name:
        return jsonify({"error": "No song name provided"}), 400

    try:
        # Options pour yt-dlp
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'static/%(title)s.%(ext)s',
            'quiet': True,
            'cookies': cookies  # Utiliser les cookies récupérés depuis les variables d'environnement
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Recherche et téléchargement de la chanson
            info_dict = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            file_name = f"{info_dict['entries'][0]['title']}.{info_dict['entries'][0]['ext']}"

        return jsonify({"success": True, "message": f"{song_name} downloaded!", "file_name": file_name})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    # Créer le dossier static si il n'existe pas
    if not os.path.exists('static'):
        os.makedirs('static')
    # Exécuter l'application
    app.run(debug=False, host="0.0.0.0", port=5000)
