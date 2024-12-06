from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import yt_dlp

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})  # Allow all origins


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
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'static/%(title)s.%(ext)s',
            'quiet': True,
            'cookiesfrombrowser': ('chrome',),  # Remplacez 'chrome' par 'firefox' ou 'edge' selon votre navigateur
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{song_name}", download=True)
            file_name = f"{info_dict['entries'][0]['title']}.{info_dict['entries'][0]['ext']}"

        return jsonify({"success": True, "message": f"{song_name} downloaded!", "file_name": file_name})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

if __name__ == "__main__":
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(debug=False, host="0.0.0.0", port=5000)
