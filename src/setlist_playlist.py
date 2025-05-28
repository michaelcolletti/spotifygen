#!/usr/bin/env python3
"""
Setlist Playlist Creator

Creates a Spotify playlist from a CSV file containing artist and song combinations.
The playlist is named "Setlist" with the current date.

Usage:
  python setlist_playlist.py setlist.csv

CSV Format:
  artist,song
  Miles Davis,All Blues
  John Coltrane,Giant Steps

Requirements:
  - Python 3.6+
  - spotipy
  - python-dotenv
  - pandas

Setup:
  1. Create a Spotify Developer account and app at https://developer.spotify.com/dashboard/
  2. Create a .env file with the following variables:
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
"""

import os
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd


def load_setlist_csv(file_path):
    """Load setlist data from CSV file with artist and song columns"""
    try:
        df = pd.read_csv(file_path)

        # Check if required columns exist (handle both orders)
        if "artist" in df.columns and "song" in df.columns:
            # Convert to list of tuples (artist, song)
            df = df.dropna(subset=["artist", "song"])
            setlist = list(zip(df["artist"].str.strip(), df["song"].str.strip()))
        elif "song" in df.columns and "artist" in df.columns:
            # Handle song,artist order
            df = df.dropna(subset=["artist", "song"])
            setlist = list(zip(df["artist"].str.strip(), df["song"].str.strip()))
        else:
            raise ValueError("CSV must contain 'artist' and 'song' columns")

        return setlist
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return None


def search_track(sp, artist, song):
    """Search for a specific track by artist and song title"""
    try:
        # Search for the track
        query = f'artist:"{artist}" track:"{song}"'
        results = sp.search(q=query, type="track", limit=10)

        if not results["tracks"]["items"]:
            # Try broader search without quotes
            query = f"{artist} {song}"
            results = sp.search(q=query, type="track", limit=10)

        if results["tracks"]["items"]:
            # Find best match - prioritize exact artist name match
            for track in results["tracks"]["items"]:
                for track_artist in track["artists"]:
                    if track_artist["name"].lower() == artist.lower():
                        return track["id"], track["name"], track_artist["name"]

            # If no exact match, return first result
            first_track = results["tracks"]["items"][0]
            return (
                first_track["id"],
                first_track["name"],
                first_track["artists"][0]["name"],
            )

        return None, None, None
    except Exception as e:
        print(f"Error searching for {artist} - {song}: {e}")
        return None, None, None


def find_todays_playlist(sp, user_id, date_str):
    """Find if today's setlist playlist already exists"""
    playlist_name = f"Setlist {date_str}"

    try:
        # Get user's playlists
        playlists = sp.user_playlists(user_id, limit=50)

        # Search through all playlists for today's setlist
        while playlists:
            for playlist in playlists["items"]:
                if (
                    playlist["name"] == playlist_name
                    and playlist["owner"]["id"] == user_id
                ):
                    return playlist["id"]

            # Check if there are more playlists to fetch
            if playlists["next"]:
                playlists = sp.next(playlists)
            else:
                break

        return None
    except Exception as e:
        print(f"Error searching for existing playlist: {e}")
        return None


def get_existing_tracks(sp, playlist_id):
    """Get all track IDs currently in the playlist"""
    try:
        existing_tracks = set()
        results = sp.playlist_tracks(playlist_id)

        while results:
            for item in results["items"]:
                if item["track"] and item["track"]["id"]:
                    existing_tracks.add(item["track"]["id"])

            if results["next"]:
                results = sp.next(results)
            else:
                break

        return existing_tracks
    except Exception as e:
        print(f"Error getting existing tracks: {e}")
        return set()


def create_or_update_setlist_playlist(sp, user_id, setlist, date_str):
    """Create a new playlist or update today's existing playlist with only new tracks"""
    playlist_name = f"Setlist {date_str}"
    playlist_description = f"Setlist playlist created/updated on {date_str}"

    try:
        # Check if today's playlist already exists
        playlist_id = find_todays_playlist(sp, user_id, date_str)
        existing_tracks = set()

        if playlist_id:
            print(f"Found existing playlist: {playlist_name}")
            print(f"Playlist ID: {playlist_id}")
            existing_tracks = get_existing_tracks(sp, playlist_id)
            print(f"Playlist currently has {len(existing_tracks)} tracks")
        else:
            # Create new playlist
            playlist = sp.user_playlist_create(
                user_id, playlist_name, public=True, description=playlist_description
            )
            playlist_id = playlist["id"]
            print(f"Created new playlist: {playlist_name}")
            print(f"Playlist ID: {playlist_id}")

        # Process each track in the setlist
        new_track_ids = []
        found_tracks = []
        not_found = []
        skipped_existing = []

        for i, (artist, song) in enumerate(setlist):
            print(f"[{i+1}/{len(setlist)}] Searching for: {artist} - {song}")

            track_id, found_song, found_artist = search_track(sp, artist, song)

            if track_id:
                if track_id in existing_tracks:
                    skipped_existing.append((artist, song, found_artist, found_song))
                    print(f"  ↻ Already in playlist: {found_artist} - {found_song}")
                else:
                    new_track_ids.append(track_id)
                    found_tracks.append((artist, song, found_artist, found_song))
                    print(f"  ✓ Found: {found_artist} - {found_song}")
            else:
                not_found.append((artist, song))
                print(f"  ✗ Not found: {artist} - {song}")

        # Add only new tracks to playlist in batches of 100
        if new_track_ids:
            for i in range(0, len(new_track_ids), 100):
                batch = new_track_ids[i : i + 100]
                sp.playlist_add_items(playlist_id, batch)

            print(f"\n✓ Added {len(new_track_ids)} new tracks to playlist")
        else:
            print(f"\n• No new tracks to add")

        # Print summary
        print(f"\n=== Setlist Playlist Summary ===")
        print(f"Playlist: {playlist_name}")
        print(f"Total tracks in CSV: {len(setlist)}")
        print(f"New tracks found and added: {len(new_track_ids)}")
        print(f"Tracks already in playlist: {len(skipped_existing)}")
        print(f"Tracks not found: {len(not_found)}")
        print(
            f"Final playlist size: {len(existing_tracks) + len(new_track_ids)} tracks"
        )

        if not_found:
            print(f"\nTracks not found:")
            for artist, song in not_found:
                print(f"  - {artist} - {song}")

        print(f"\nPlaylist URL: https://open.spotify.com/playlist/{playlist_id}")

        return playlist_id

    except Exception as e:
        print(f"Error creating playlist: {e}")
        return None


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Create a Spotify playlist from a CSV setlist file."
    )
    parser.add_argument(
        "file",
        help="Path to CSV file containing setlist (must have 'artist' and 'song' columns)",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check for required environment variables (try both SPOTIFY_ and SPOTIPY_ prefixes)
    client_id = os.getenv("SPOTIFY_CLIENT_ID") or os.getenv("SPOTIPY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET") or os.getenv(
        "SPOTIPY_CLIENT_SECRET"
    )
    redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI") or os.getenv(
        "SPOTIPY_REDIRECT_URI"
    )

    missing_vars = []
    if not client_id:
        missing_vars.append("SPOTIFY_CLIENT_ID or SPOTIPY_CLIENT_ID")
    if not client_secret:
        missing_vars.append("SPOTIFY_CLIENT_SECRET or SPOTIPY_CLIENT_SECRET")
    if not redirect_uri:
        missing_vars.append("SPOTIFY_REDIRECT_URI or SPOTIPY_REDIRECT_URI")

    if missing_vars:
        print(
            f"Error: Missing required environment variables: {', '.join(missing_vars)}"
        )
        print(
            "Please create a .env file with these variables or set them in your environment."
        )
        sys.exit(1)

    # Initialize Spotify client
    try:
        sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="playlist-modify-public",
            )
        )
        user_id = sp.current_user()["id"]
        print(f"Authenticated as: {user_id}")
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)

    # Load setlist from CSV
    setlist = load_setlist_csv(args.file)
    if not setlist:
        print("Error: Could not load setlist from CSV file.")
        sys.exit(1)

    print(f"Loaded {len(setlist)} tracks from setlist")

    # Get current date for playlist name
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Create or update the playlist
    playlist_id = create_or_update_setlist_playlist(sp, user_id, setlist, date_str)

    if not playlist_id:
        print("Failed to create playlist")
        sys.exit(1)


if __name__ == "__main__":
    main()
