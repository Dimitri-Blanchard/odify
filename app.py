from flask import Flask, request, jsonify
import yt_dlp
import os
import logging
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Global yt_dlp options for reuse
ydl_opts = {
    'format': 'bestaudio/best',  # Choisit le meilleur format audio disponible
    'quiet': True,  # Désactive les logs détaillés
    'noplaylist': True,  # Ne télécharge pas les playlists, seulement la première vidéo
    'outtmpl': '%(id)s.%(ext)s',  # Modifie le nom du fichier de sortie en fonction de l'ID de la vidéo
    'restrictfilenames': True  # Limite les noms de fichiers pour éviter les problèmes
}

def get_youtube_download_url(song_name: str):
    """
    Helper function to extract download URL from YouTube search.
    """
    try:
        app.logger.info(f"Searching for song: {song_name}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            video_info = info_dict['entries'][0]
            file_url = video_info.get('url')
            app.logger.info(f"Song found: {video_info.get('title')}, URL: {file_url}")
            return file_url, video_info
    except yt_dlp.utils.DownloadError as e:
        app.logger.error(f"yt-dlp error: {str(e)}")
        raise Exception("Error fetching song details from YouTube.")
    except Exception as e:
        app.logger.error(f"General error fetching song details: {str(e)}")
        raise Exception("Error fetching song details from YouTube.")

@app.route("/download", methods=["POST"])
def download_song():
    """
    Endpoint to get a direct download link for a song based on its name.
    """
    data = request.json
    song_name = data.get("song_name")

    if not song_name:
        app.logger.error("No song name provided.")
        return jsonify({"error": "No song name provided"}), 400

    if len(song_name) > 200:  # Example of input validation
        app.logger.error(f"Song name is too long: {len(song_name)} characters.")
        return jsonify({"error": "Song name is too long. Please limit it to 200 characters."}), 400

    try:
        app.logger.info(f"Fetching song details for: {song_name}")
        file_url, video_info = get_youtube_download_url(song_name)

        app.logger.info(f"Song details fetched successfully: {video_info.get('title')}")
        return jsonify({
            "success": True,
            "download_url": file_url,
            "title": video_info.get('title', 'Unknown Title'),
            "source": video_info.get("webpage_url", "")
        })

    except Exception as e:
        app.logger.error(f"Error occurred: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # If in production, set debug to False
    app.run(debug=os.environ.get("FLASK_ENV") == "development")
