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
    'format': 'bestaudio/best',
    'quiet': True,
    'noplaylist': True,
    'outtmpl': '%(id)s.%(ext)s',
    'restrictfilenames': True
}

def get_youtube_download_url(song_name: str):
    """
    Helper function to extract download URL from YouTube search.
    """
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(f"ytsearch:{song_name}", download=False)
            video_info = info_dict['entries'][0]
            file_url = video_info.get('url')
            return file_url, video_info
    except Exception as e:
        logging.error(f"Error fetching song details: {str(e)}")
        raise Exception("Error fetching song details from YouTube.")

@app.route("/download", methods=["POST"])
def download_song():
    """
    Endpoint to get a direct download link for a song based on its name.
    """
    data = request.json
    song_name = data.get("song_name")

    if not song_name:
        return jsonify({"error": "No song name provided"}), 400

    if len(song_name) > 200:  # Example of input validation
        return jsonify({"error": "Song name is too long. Please limit it to 200 characters."}), 400

    try:
        file_url, video_info = get_youtube_download_url(song_name)

        return jsonify({
            "success": True,
            "download_url": file_url,
            "title": video_info.get('title', 'Unknown Title'),
            "source": video_info.get("webpage_url", "")
        })

    except Exception as e:
        # Provide a user-friendly error message
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    # If in production, set debug to False
    app.run(debug=os.environ.get("FLASK_ENV") == "development")
