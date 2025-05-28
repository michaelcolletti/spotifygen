## SpotifyGen 
**SpotifyGen** is a collection of Python scripts designed to help you manage and generate Spotify playlists. 🎧

These scripts offer multiple ways to create and organize your Spotify library, from artist-based discovery to exact setlist recreation.

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
    SpotifyGen requires your API credentials. Create a `.env` file in the project root:
    ```bash
    # .env file
    SPOTIPY_CLIENT_ID=your_client_id_here
    SPOTIPY_CLIENT_SECRET=your_client_secret_here
    SPOTIPY_REDIRECT_URI=http://localhost:8888/callback
    ```
    
    Or set them in your shell environment:
    ```bash
    export SPOTIPY_CLIENT_ID='YOUR_CLIENT_ID'
    export SPOTIPY_CLIENT_SECRET='YOUR_CLIENT_SECRET'
    export SPOTIPY_REDIRECT_URI='YOUR_REDIRECT_URI'
    ```
    
    **Note**: Scripts support both `SPOTIFY_*` and `SPOTIPY_*` prefixes for compatibility.
    
    A way to convert env to GH secrets is [env-to-github-secrets](https://github.com/michaelcolletti/env-to-github-secrets/).

## 🚀 Usage

SpotifyGen offers several scripts for different playlist creation workflows:

---

<details>
<summary>🎵 <code>spotifygenCLI.py</code> - Artist-Based Playlist Creator</summary>

Creates two playlists from a list of artists: one with popular tracks and another with deep cuts (lesser-known tracks).

**How it Works:**
Provide a text file with artist names (one per line), and the script will create two playlists using Spotify's catalog.

**Command Line Arguments:**

*   `file`: Path to text file containing artist names (Required)
*   `--popular-limit INTEGER`: Number of popular tracks per artist (Default: 3)
*   `--deep-limit INTEGER`: Number of deep cuts per artist (Default: 3)
*   `--country COUNTRY`: Country code for popularity metrics (Default: US)
*   `--popular-name TEXT`: Name for the popular tracks playlist
*   `--deep-name TEXT`: Name for the deep cuts playlist

**Example:**
Create playlists from artists listed in `artist-list.txt` with 5 popular tracks and 2 deep cuts per artist:

```bash
python src/spotifygenCLI.py artist-list.txt \
  --popular-limit 5 \
  --deep-limit 2 \
  --popular-name "Top Hits Collection" \
  --deep-name "Hidden Gems"
```

**Output:**
- "Top Hits Collection" playlist with popular tracks
- "Hidden Gems" playlist with lesser-known tracks
- Summary report with success/failure counts
</details>

---

<details>
<summary>📝 <code>setlist_playlist.py</code> - CSV Setlist Creator</summary>

Creates or updates a daily playlist from a CSV file containing exact artist-song combinations.

**How it Works:**
Provide a CSV file with `artist` and `song` columns, and the script will search for exact matches and create a dated playlist.

**Smart Update Logic:**
- **Same day:** Updates existing "Setlist YYYY-MM-DD" playlist with only new tracks
- **New day:** Creates fresh playlist for the current date
- **Duplicate detection:** Skips songs already in the playlist

**Command Line Arguments:**

*   `file`: Path to CSV file containing setlist (Required)

**CSV Format:**
```csv
song,artist
Dolphin Dance,Herbie Hancock
So What,Miles Davis
Giant Steps,John Coltrane
```

**Example:**
```bash
python src/setlist_playlist.py setlist.csv
```

**Output:**
- "Setlist 2025-05-28" playlist with exact track matches
- Real-time search progress with ✓/✗/↻ indicators
- Detailed summary showing new vs existing tracks
- Direct Spotify playlist URL

**Features:**
- **Exact matching:** Searches for specific artist-song combinations
- **Fallback search:** Uses broader search if exact match fails
- **Progress tracking:** Shows search results for each track
- **Environment flexible:** Works with both `SPOTIFY_*` and `SPOTIPY_*` variables
</details>

---

<details>
<summary>🔄 <code>spotifygen.py</code> - Interactive Artist Processor</summary>

Interactive version of the artist-based playlist creator with user prompts.

**How it Works:**
Run the script and it will prompt you for an artist list file, then create both popular and deep cuts playlists.

**Example:**
```bash
python src/spotifygen.py
# Enter the path to your text file containing artists: artist-list.txt
```

**Output:**
- "Most Popular Tracks" playlist
- "Deep Cuts Collection" playlist
- Interactive progress updates
</details>

---

## 📁 File Formats

### Artist List Format (for `spotifygenCLI.py` and `spotifygen.py`)
Plain text file with one artist name per line:
```
Miles Davis
John Coltrane
Herbie Hancock
Wayne Shorter
```

### CSV Setlist Format (for `setlist_playlist.py`)
CSV file with `song` and `artist` columns:
```csv
song,artist
Blue in Green,Miles Davis
Giant Steps,John Coltrane
Maiden Voyage,Herbie Hancock
```

## 🛠️ Development Commands

SpotifyGen includes a Makefile for common development tasks:

```bash
make install    # Install dependencies
make test      # Run pytest tests
make lint      # Run pylint on test files
make format    # Format code with black
make clean     # Remove cache directories
make all       # Run install, lint, test, and format
```

## 🐳 Docker Support

SpotifyGen can be containerized for consistent deployment:

```bash
# Build the Docker image
docker build -t spotifygen .

# Run with environment variables
docker run -e SPOTIPY_CLIENT_ID=your_id \
           -e SPOTIPY_CLIENT_SECRET=your_secret \
           -e SPOTIPY_REDIRECT_URI=http://localhost:8888/callback \
           -v $(pwd):/app \
           spotifygen python src/setlist_playlist.py setlist.csv

# Run interactive shell in container
docker run -it spotifygen bash
```

**Docker Features:**
- Python 3.11-slim base image for optimal size
- Development tools included (pytest, pylint, black)
- Layer caching for faster builds
- Proper environment variable support

## 💡 Tips & Tricks

*   **Finding Spotify IDs/URIs**: You can find Spotify URIs/IDs by clicking the "..." (three dots) next to a song, artist, album, or playlist in the Spotify app/website, then "Share" -> "Copy Spotify URI" or "Copy Link".
    *   Example URI: `spotify:track:TRACK_ID`
    *   Example Link: `https://open.spotify.com/track/TRACK_ID?si=...`
    *   The `TRACK_ID` is the alphanumeric string you need.

*   **Rate Limiting**: Spotify's API has rate limits. The scripts include built-in delays (1 second between artists, 0.1 seconds for track requests) to avoid hitting these limits.

*   **Authentication Flow**: The first time you run a script, you'll be redirected to a Spotify login page in your browser to grant permission. Subsequent runs use a cached token.

*   **Environment Variables**: Scripts support both `SPOTIFY_*` and `SPOTIPY_*` prefixes for environment variables, making them compatible with existing setups.

*   **Daily Workflow**: Use `setlist_playlist.py` with the same CSV file throughout the day to incrementally build your setlist - it will only add new tracks!

*   **Large Artist Lists**: For processing many artists, the scripts include progress indicators and error handling to track which artists couldn't be found.

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