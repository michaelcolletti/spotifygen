#!/usr/bin/env python3
"""
Spotify Playlist Creator CLI Tool

This script creates two Spotify playlists from a text file containing artist names:
1. A playlist with each artist's most popular tracks
2. A playlist with each artist's deep cuts (lesser-known tracks)

Usage:
  python spotify_playlist_creator.py path/to/artists.txt

Requirements:
  - Python 3.6+
  - spotipy
  - python-dotenv

Setup:
  1. Create a Spotify Developer account and app at https://developer.spotify.com/dashboard/
  2. Create a .env file with the following variables:
     SPOTIFY_CLIENT_ID=your_client_id
     SPOTIFY_CLIENT_SECRET=your_client_secret
     SPOTIFY_REDIRECT_URI=http://localhost:8888/callback
"""

import os
import sys
import time
import argparse
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Create Spotify playlists from a list of artists."
    )
    parser.add_argument(
        "file", help="Path to text file containing artist names (one per line)"
    )
    parser.add_argument(
        "--popular-limit",
        type=int,
        default=3,
        help="Number of popular tracks per artist (default: 3)",
    )
    parser.add_argument(
        "--deep-limit",
        type=int,
        default=3,
        help="Number of deep cuts per artist (default: 3)",
    )
    parser.add_argument(
        "--country",
        default="US",
        help="Country code for popularity metrics (default: US)",
    )
    parser.add_argument(
        "--popular-name",
        default="Most Popular Tracks",
        help="Name for the popular tracks playlist",
    )
    parser.add_argument(
        "--deep-name",
        default="Deep Cuts Collection",
        help="Name for the deep cuts playlist",
    )

    args = parser.parse_args()

    # Load environment variables
    load_dotenv()

    # Check for required environment variables
    required_vars = [
        "SPOTIFY_CLIENT_ID",
        "SPOTIFY_CLIENT_SECRET",
        "SPOTIFY_REDIRECT_URI",
    ]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

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
                client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                scope="playlist-modify-public user-library-read",
            )
        )
        user_id = sp.current_user()["id"]
        print(f"Authenticated as: {user_id}")
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)

    # Read artists file
    try:
        with open(args.file, "r") as file:
            artists = [line.strip() for line in file.readlines()]
            artists = [artist for artist in artists if artist]

        if not artists:
            print("Error: No artists found in the file.")
            sys.exit(1)

        print(f"Found {len(artists)} artists in file")
        if len(artists) > 5:
            print(f"First 5 artists: {', '.join(artists[:5])}...")
        else:
            print(f"Artists: {', '.join(artists)}")
    except FileNotFoundError:
        print(f"Error: File '{args.file}' not found.")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    # Create playlists
    try:
        popular_playlist = sp.user_playlist_create(
            user_id,
            args.popular_name,
            public=True,
            description=f"A collection of the most popular tracks from my favorite artists",
        )
        deep_cuts_playlist = sp.user_playlist_create(
            user_id,
            args.deep_name,
            public=True,
            description=f"Lesser-known gems from my favorite artists",
        )

        popular_playlist_id = popular_playlist["id"]
        deep_cuts_playlist_id = deep_cuts_playlist["id"]

        print(f"Created playlist '{args.popular_name}' with ID: {popular_playlist_id}")
        print(f"Created playlist '{args.deep_name}' with ID: {deep_cuts_playlist_id}")
    except Exception as e:
        print(f"Error creating playlists: {e}")
        sys.exit(1)

    # Process artists
    popular_tracks = []
    deep_cut_tracks = []
    skipped_artists = []

    for i, artist in enumerate(artists):
        print(f"[{i+1}/{len(artists)}] Processing artist: {artist}")

        try:
            # Find artist ID
            results = sp.search(q=f"artist:{artist}", type="artist", limit=1)
            if not results["artists"]["items"]:
                print(f"  Could not find artist: {artist}")
                skipped_artists.append(artist)
                continue

            artist_id = results["artists"]["items"][0]["id"]
            matched_name = results["artists"]["items"][0]["name"]
            print(f"  Found artist: {matched_name}")

            # Get top tracks
            top_tracks = sp.artist_top_tracks(artist_id, args.country)["tracks"][
                : args.popular_limit
            ]
            top_track_ids = [track["id"] for track in top_tracks]
            popular_tracks.extend(top_track_ids)

            # Get deep cuts
            albums = []
            album_results = sp.artist_albums(artist_id, album_type="album", limit=50)
            albums.extend(album_results["items"])

            # Handle pagination for albums
            while album_results["next"]:
                album_results = sp.next(album_results)
                albums.extend(album_results["items"])

            # Get unique albums
            unique_albums = {}
            for album in albums:
                if album["name"].lower() not in unique_albums:
                    unique_albums[album["name"].lower()] = album["id"]

            # Collect tracks
            all_tracks = []
            for album_id in list(unique_albums.values())[:5]:  # Limit to 5 albums
                track_results = sp.album_tracks(album_id)
                all_tracks.extend(track_results["items"])

                while track_results["next"]:
                    track_results = sp.next(track_results)
                    all_tracks.extend(track_results["items"])

            # Get full track info for popularity
            track_info = []
            for track in all_tracks[
                :50
            ]:  # Limit to 50 tracks per artist to avoid rate limits
                try:
                    full_track = sp.track(track["id"])
                    track_info.append(full_track)
                    time.sleep(0.1)  # Avoid rate limits
                except:
                    continue

            # Sort by popularity (ascending) for deep cuts
            track_info.sort(key=lambda x: x["popularity"])
            deep_cuts = track_info[: args.deep_limit]
            deep_cut_ids = [track["id"] for track in deep_cuts]
            deep_cut_tracks.extend(deep_cut_ids)

            print(
                f"  Added {len(top_track_ids)} popular tracks and {len(deep_cut_ids)} deep cuts"
            )

        except Exception as e:
            print(f"  Error processing artist {artist}: {e}")

        # Add a small delay
        time.sleep(1)

    # Add tracks to playlists in batches
    try:
        for i in range(0, len(popular_tracks), 100):
            batch = popular_tracks[i : i + 100]
            sp.playlist_add_items(popular_playlist_id, batch)

        for i in range(0, len(deep_cut_tracks), 100):
            batch = deep_cut_tracks[i : i + 100]
            sp.playlist_add_items(deep_cuts_playlist_id, batch)
    except Exception as e:
        print(f"Error adding tracks to playlists: {e}")

    # Print summary
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


if __name__ == "__main__":
    main()
