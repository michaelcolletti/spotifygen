# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Development Commands:**
- `make install` - Install dependencies from requirements.txt
- `make test` - Run pytest tests for spotifygen.py and spotifygenCLI.py
- `make lint` - Run pylint on test files  
- `make format` - Format source code with black
- `make clean` - Remove cache directories and build artifacts
- `make all` - Run install, lint, test, and format in sequence

**Running the Application:**
- CLI: `python src/spotifygenCLI.py artist-list.txt`
- Interactive: `python src/spotifygen.py` (prompts for file path)

## Architecture

SpotifyGen creates Spotify playlists from artist lists with two main execution paths:

**Core Modules:**
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

**Authentication:**
Requires environment variables: `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `SPOTIFY_REDIRECT_URI`
Uses SpotifyOAuth with scopes: "playlist-modify-public user-library-read"

**Rate Limiting:**
- 1-second delays between artist processing
- 0.1-second delays for track metadata requests  
- Batches track uploads in groups of 100 (Spotify API limit)
- Limits album scanning to 5 albums per artist