# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Development Commands:**
- `make install` - Install dependencies from requirements.txt (with --no-cache-dir for Docker)
- `make test` - Run pytest tests for spotifygen.py and spotifygenCLI.py
- `make lint` - Run pylint on test files  
- `make format` - Format source code with black
- `make clean` - Remove cache directories and build artifacts
- `make all` - Run install, lint, test, and format in sequence

**Running the Applications:**
- **Artist-based CLI:** `python src/spotifygenCLI.py artist-list.txt`
- **CSV Setlist:** `python src/setlist_playlist.py setlist.csv`
- **Interactive:** `python src/spotifygen.py` (prompts for file path)

**Docker Commands:**
- `docker build -t spotifygen .` - Build Docker image
- `docker run -v $(pwd):/app spotifygen` - Run container with volume mount

## Architecture

SpotifyGen offers three distinct playlist creation workflows:

### 1. Artist-Based Playlist Generation
**Modules:**
- `src/spotifygen.py` - Interactive script version with user input prompts
- `src/spotifygenCLI.py` - Command-line interface with argument parsing
- `src/main.py` - Alternative interactive entry point (legacy)

**Key Functions (shared logic):**
- `read_artists_from_file()` - Parse artist names from text files
- `find_artist_id()` - Search Spotify API for artist matches  
- `get_top_tracks()` - Retrieve popular tracks by artist
- `get_deep_cuts()` - Find lesser-known tracks from album catalogs
- `create_playlist()` - Generate new Spotify playlists
- `add_tracks_to_playlist()` - Batch add tracks (handles 100-track API limit)

**Data Flow:**
1. Read artist names from text file (one per line)
2. Search Spotify API for each artist ID
3. Collect popular tracks and deep cuts in parallel
4. Create two playlists: "Most Popular Tracks" and "Deep Cuts Collection"
5. Batch upload tracks to playlists (respecting API limits)

### 2. CSV Setlist Playlist Creation
**Module:** `src/setlist_playlist.py`

**Key Functions:**
- `load_setlist_csv()` - Parse CSV files with artist/song columns
- `search_track()` - Find exact artist-song matches with fallback search
- `find_todays_playlist()` - Search for existing daily playlists
- `get_existing_tracks()` - Retrieve current playlist contents
- `create_or_update_setlist_playlist()` - Smart playlist creation/updating

**Smart Update Logic:**
- **Same day:** Updates existing "Setlist YYYY-MM-DD" playlist with only new tracks
- **New day:** Creates fresh playlist for current date
- **Duplicate detection:** Skips songs already in playlist

**Data Flow:**
1. Parse CSV file with artist,song columns
2. Check if today's playlist exists
3. Get existing tracks (if playlist exists)
4. Search for each artist-song combination
5. Add only new tracks to playlist
6. Provide detailed progress and summary

### 3. Environment & Authentication
**Environment Variables:** 
- Supports both `SPOTIFY_*` and `SPOTIPY_*` prefixes for compatibility
- Required: `CLIENT_ID`, `CLIENT_SECRET`, `REDIRECT_URI`

**Authentication:**
- Uses SpotifyOAuth with appropriate scopes
- Artist-based: "playlist-modify-public user-library-read"  
- Setlist: "playlist-modify-public"

### 4. Rate Limiting & API Management
- 1-second delays between artist processing
- 0.1-second delays for track metadata requests  
- Batches track uploads in groups of 100 (Spotify API limit)
- Limits album scanning to 5 albums per artist (for deep cuts)

### 5. Containerization
**Docker Support:**
- Python 3.11-slim base image
- Multi-stage build with dependency caching
- Development tools included (test, lint, format)
- Environment variable support for credentials