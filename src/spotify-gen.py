# Spotify Playlist Creator
# This notebook creates two playlists from a list of artists:
# 1. Popular tracks playlist
# 2. Deep cuts playlist

import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# 1. Set up authentication with Spotify API
# You'll need to create a Spotify Developer account and register an application
# to get these credentials: https://developer.spotify.com/dashboard/
# Then store them in a .env file or system environment variables

# Get credentials from environment variables
client_id = os.getenv("SPOTIFY_CLIENT_ID")
client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI", "http://localhost:8888/callback")

# Define required scopes for playlist creation
scope = "playlist-modify-public user-library-read"

# Create the Spotify client
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope=scope,
    )
)

# Get user ID (needed for playlist creation)
user_id = sp.current_user()["id"]
print(f"Authenticated as: {user_id}")


# 2. Read artists from text file
def read_artists_from_file(file_path):
    with open(file_path, "r") as file:
        # Read lines and strip whitespace
        artists = [line.strip() for line in file.readlines()]
        # Filter out empty lines
        artists = [artist for artist in artists if artist]
    return artists


# Example: './artists.txt'
file_path = input("Enter the path to your text file containing artists: ")
artists = read_artists_from_file(file_path)
print(f"Found {len(artists)} artists in file")
print(f"First 5 artists: {artists[:5]}")


# 3. Functions to find artists and their tracks
def find_artist_id(artist_name):
    """Search for an artist and return their Spotify ID"""
    results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
    if results["artists"]["items"]:
        artist_id = results["artists"]["items"][0]["id"]
        artist_name = results["artists"]["items"][0]["name"]
        return artist_id, artist_name
    return None, None


def get_top_tracks(artist_id, country="US", limit=3):
    """Get an artist's top tracks"""
    results = sp.artist_top_tracks(artist_id, country)
    return results["tracks"][:limit]


def get_deep_cuts(artist_id, limit=3):
    """Get deep cuts (less popular tracks) from an artist's albums"""
    # Get all albums by the artist
    albums = []
    results = sp.artist_albums(artist_id, album_type="album", limit=50)
    albums.extend(results["items"])

    # Handle potential pagination (if artist has many albums)
    while results["next"]:
        results = sp.next(results)
        albums.extend(results["items"])

    # Get unique album IDs (avoiding duplicates like deluxe editions)
    unique_albums = {}
    for album in albums:
        if album["name"].lower() not in unique_albums:
            unique_albums[album["name"].lower()] = album["id"]

    # Collect all tracks from albums
    all_tracks = []
    for album_id in list(unique_albums.values())[
        :5
    ]:  # Limit to first 5 albums to avoid API rate limits
        results = sp.album_tracks(album_id)
        all_tracks.extend(results["items"])

        # Handle potential pagination
        while results["next"]:
            results = sp.next(results)
            all_tracks.extend(results["items"])

    # Sort tracks by popularity (ascending)
    track_info = []
    for track in all_tracks:
        # Get full track info to access popularity
        try:
            full_track = sp.track(track["id"])
            track_info.append(full_track)
        except:
            # Skip if we hit API rate limits
            continue
        time.sleep(0.1)  # Avoid hitting API rate limits

    # Sort by popularity (ascending) and take the least popular tracks
    track_info.sort(key=lambda x: x["popularity"])
    return track_info[:limit]


# 4. Create playlists
def create_playlist(name, description):
    """Create a new playlist and return its ID"""
    playlist = sp.user_playlist_create(
        user_id, name, public=True, description=description
    )
    return playlist["id"]


# Create the two playlists
popular_playlist_id = create_playlist(
    "Most Popular Tracks",
    "A collection of the most popular tracks from my favorite artists",
)
deep_cuts_playlist_id = create_playlist(
    "Deep Cuts Collection", "Lesser-known gems from my favorite artists"
)

print(f"Created playlist 'Most Popular Tracks' with ID: {popular_playlist_id}")
print(f"Created playlist 'Deep Cuts Collection' with ID: {deep_cuts_playlist_id}")

# 5. Process each artist and add tracks to playlists
popular_tracks = []
deep_cut_tracks = []
skipped_artists = []

for artist in artists:
    print(f"Processing artist: {artist}")

    # Find the artist
    artist_id, matched_name = find_artist_id(artist)
    if not artist_id:
        print(f"Could not find artist: {artist}")
        skipped_artists.append(artist)
        continue

    print(f"Found artist: {matched_name} (ID: {artist_id})")

    # Get top tracks
    top_tracks = get_top_tracks(artist_id)
    top_track_ids = [track["id"] for track in top_tracks]
    popular_tracks.extend(top_track_ids)

    # Get deep cuts
    try:
        cuts = get_deep_cuts(artist_id)
        cut_ids = [track["id"] for track in cuts]
        deep_cut_tracks.extend(cut_ids)

        print(
            f"Added {len(top_tracks)} popular tracks and {len(cuts)} deep cuts for {matched_name}"
        )
    except Exception as e:
        print(f"Error getting deep cuts for {matched_name}: {e}")

    # Add a small delay to avoid hitting API rate limits
    time.sleep(1)


# 6. Add tracks to playlists
# Spotify API limits: maximum of 100 tracks per request
def add_tracks_to_playlist(playlist_id, track_ids):
    """Add tracks to a playlist in batches of 100"""
    for i in range(0, len(track_ids), 100):
        batch = track_ids[i : i + 100]
        sp.playlist_add_items(playlist_id, batch)


add_tracks_to_playlist(popular_playlist_id, popular_tracks)
add_tracks_to_playlist(deep_cuts_playlist_id, deep_cut_tracks)

# 7. Summary
print("\n=== Playlist Creation Summary ===")
print(f"Total artists processed: {len(artists) - len(skipped_artists)}")
print(f"Skipped artists: {len(skipped_artists)}")
if skipped_artists:
    print(f"Skipped artist names: {', '.join(skipped_artists)}")
print(f"Total tracks in popular playlist: {len(popular_tracks)}")
print(f"Total tracks in deep cuts playlist: {len(deep_cut_tracks)}")
print("\nPlaylist URLs:")
print(f"Popular Tracks: https://open.spotify.com/playlist/{popular_playlist_id}")
print(f"Deep Cuts: https://open.spotify.com/playlist/{deep_cuts_playlist_id}")

# Example file format for artists.txt:
# Taylor Swift
# The Beatles
# Kendrick Lamar
# Beyoncé
# Radiohead
