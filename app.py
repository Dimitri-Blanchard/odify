from flask import Flask, request, jsonify
import yt_dlp
import os
import logging
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

logging.basicConfig(level=logging.INFO)

ydl_opts = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'outtmpl': '%(id)s.%(ext)s',
    'restrictfilenames': True
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

    if len(song_name) > 200:
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
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.environ.get("FLASK_ENV") == "development")
