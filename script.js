const downloadBtn = document.getElementById('downloadBtn');
const songInput = document.getElementById('songInput');
const responseMessage = document.getElementById('responseMessage');
const API_URL = "http://127.0.0.1:5000/download";

// Utility function to update response message
const updateResponseMessage = (message, color) => {
    responseMessage.textContent = message;
    responseMessage.style.color = color;
};

downloadBtn.addEventListener('click', async () => {
    const songName = songInput.value.trim();

    // Early exit if no song name is provided
    if (!songName) {
        return updateResponseMessage("Please enter a song name.", "red");
    }

    updateResponseMessage("Searching...", "white");

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ song_name: songName }),
        });

        const data = await response.json();

        if (!data.success) throw new Error(data.error);

        // Handle successful response
        updateResponseMessage(`Downloading and playing "${data.title}"...`, "green");

        const audioElement = new Audio(data.download_url);

        audioElement.play();

        audioElement.onplay = () => {
            updateResponseMessage(`Now playing: "${data.title}"`, "green");
        };

        audioElement.onerror = (err) => {
            updateResponseMessage(`Error playing the audio: ${err.message}`, "red");
        };

    } catch (error) {
        updateResponseMessage(`Error: ${error.message}`, "red");
    }
});
