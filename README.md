## SpotifyGen 
## SpotifyGen
**SpotifyGen** is a collection of scripts designed to help you manage and generate Spotify playlists. 🎧

These scripts assist in creating and organizing your Spotify library.

## 🚦 Prerequisites

Before using SpotifyGen, ensure you have the following:

*   🐍 **Python 3.7+**: Ensure your Python version is 3.7 or higher.
*   🔑 **Spotify Developer Account & API Credentials**:
    *   Go to the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
    *   Create an app to get your `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET`.
    *   Set your `SPOTIPY_REDIRECT_URI` (e.g., `http://localhost:8888/callback` or any other valid URI).
*   📦 **Required Python Packages**: These will be installed during setup.

## 🛠️ Setup & Installation

Follow these steps to set up SpotifyGen.

1.  **Clone the Repository** (if you haven't already):
    ```bash
    git clone https://github.com/michaelcolletti/spotifygen.git
    cd spotifygen
    ```

2.  **Install Dependencies**:
    It's highly recommended to use a virtual environment:
    ```bash
    python -m venv .venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
    Then install the necessary packages (assuming a `requirements.txt` file):
    ```bash
    pip install -r requirements.txt
    ```
    If no `requirements.txt` exists, you'll likely need `spotipy`:
    ```bash
    pip install spotipy
    ```

3.  **Set Environment Variables**:
    SpotifyGen requires your API credentials. You can set these in your shell environment or use .env. A way to convert env to GH secrets is [env-to-github-secrets](https://github.com/michaelcolletti/env-to-github-secrets/):
    ```bash
    export SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
    export SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
    export SPOTIPY_REDIRECT_URI='YOUR_REDIRECT_URI'
    ```
    (On Windows, use `set` instead of `export`, e.g., `set SPOTIPY_CLIENT_ID=YOUR_CLIENT_ID`)
    Alternatively, consider using a `.env` file with a library like `python-dotenv` if the scripts support it.

## 🚀 Usage

This section explains how to use the scripts. Each script (or module) has specific functionalities. The following are *hypothetical* examples. Adapt these to your actual script names and functionalities.

---

<details>
<summary>✨ <code>create_playlist.py</code> - Create New Playlists</summary>

This script creates new playlists based on specified artists, genres, or tracks.

**How it Works:**
Provide seed artists, genres, and/or tracks, and the script will use Spotify's recommendation engine to generate a list of songs.

**Command Line Arguments (Example):**

*   `--name TEXT`: Name of the new playlist (Required).
*   `--seeds-artists TEXT,...`: Comma-separated list of Spotify artist IDs or names.
*   `--seeds-genres TEXT,...`: Comma-separated list of Spotify genre strings (e.g., "pop,rock,indie").
*   `--seeds-tracks TEXT,...`: Comma-separated list of Spotify track IDs.
*   `--limit INTEGER`: Number of tracks to add (Default: 20).
*   `--public BOOLEAN`: Make playlist public (Default: True, use `--no-public` for False).
*   `--description TEXT`: Playlist description.

**Example:**
Create a 30-track public playlist named "Indie Vibes" based on artists "Bon Iver", "The National", and the genre "indie-folk".

```bash
python scripts/create_playlist.py \
  --name "Indie Vibes" \
  --seeds-artists "Bon Iver,The National" \
  --seeds-genres "indie-folk" \
  --limit 30 \
  --description "Chill indie folk tunes for a rainy day."
```
</details>

---

<details>
<summary>❤️ <code>populate_from_liked.py</code> - Populate Playlists from Liked Songs</summary>

This script filters your liked songs based on specific criteria and adds matching tracks to a target playlist. This is useful for creating mood-based playlists from your existing favorites.

**How it Works:**
Specify criteria like genre, artist, or audio features (e.g., danceability, energy) to filter your liked songs.

**Command Line Arguments (Example):**

*   `--playlist-id TEXT`: ID of the playlist to add tracks to (Required).
*   `--min-danceability FLOAT`: Minimum danceability (0.0 to 1.0).
*   `--max-valence FLOAT`: Maximum valence (musical positiveness, 0.0 to 1.0).
*   `--artist TEXT`: Filter by a specific artist name.
*   `--genre TEXT`: Filter by a specific genre (Note: Spotify's genre tagging on tracks can be broad).
*   `--limit INTEGER`: Max number of tracks to add from liked songs (Default: 50).

**Example:**
Add up to 25 highly danceable tracks by "Daft Punk" from your liked songs to the playlist with ID `37i9dQZF1DXcBWIGoYBM5M`.

```bash
python scripts/populate_from_liked.py \
  --playlist-id "37i9dQZF1DXcBWIGoYBM5M" \
  --artist "Daft Punk" \
  --min-danceability 0.7 \
  --limit 25
```
</details>

---

<details>
<summary>📊 <code>analyze_playlist.py</code> - Analyze Playlist Data</summary>

This script provides statistics and audio feature averages for a given playlist. For example, you can find the average danceability of a workout mix or the most common artist in a "Chill Focus" playlist.

**How it Works:**
Provide a playlist ID, and the script will output statistics and audio feature averages.

**Command Line Arguments (Example):**

*   `--playlist-id TEXT`: ID of the playlist to analyze (Required).
*   `--output-format TEXT`: Output format (`json`, `csv`, `pretty`) (Default: `pretty`).

**Example:**
Analyze the playlist `37i9dQZF1DX4sWSpwq3LiO` and display the results in a human-readable format.

```bash
python scripts/analyze_playlist.py \
  --playlist-id "37i9dQZF1DX4sWSpwq3LiO" \
  --output-format pretty
```
This might show you:
*   Total Tracks: 50
*   Average Danceability: 0.65
*   Average Energy: 0.72
*   Top 3 Artists: Artist A (5 tracks), Artist B (4 tracks), Artist C (3 tracks)
*   Top 3 Genres (derived from artists): pop, electro-pop, dance
</details>

---

## 💡 Tips & Tricks

*   **Finding Spotify IDs/URIs**: You can find Spotify URIs/IDs by clicking the "..." (three dots) next to a song, artist, album, or playlist in the Spotify app/website, then "Share" -> "Copy Spotify URI" or "Copy Link".
    *   Example URI: `spotify:track:TRACK_ID`
    *   Example Link: `https://open.spotify.com/track/TRACK_ID?si=...`
    *   The `TRACK_ID` is the alphanumeric string you need.
*   **Rate Limiting**: Spotify's API has rate limits. If you're processing large libraries or making many requests quickly, the scripts might encounter these. Be patient, or design your scripts to handle them (e.g., with retries and backoff).
*   **Authentication Flow**: The first time you run a script that requires user authorization (like modifying playlists or accessing user private data), you'll likely be redirected to a Spotify login page in your browser to grant permission. Subsequent runs might use a cached token.

## 🤝 Contributing

Contributions to improve SpotifyGen are welcome!
1.  Fork the repository.
2.  Create your feature branch (`git checkout -b feature/AmazingFeature`).
3.  Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4.  Push to the branch (`git push origin feature/AmazingFeature`).
5.  Open a Pull Request.

Please make sure your code adheres to any existing style guidelines and includes tests where appropriate.

## 📜 License

Distributed under the MIT License. See `LICENSE` file for more information (if one exists in your project).

---

Happy playlisting! 🎉