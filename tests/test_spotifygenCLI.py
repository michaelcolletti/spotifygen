import os
import sys
import time
import argparse
import pytest
from unittest import mock
from io import StringIO
import spotipy
from dotenv import load_dotenv

# Add the src directory to the path so we can import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
import src.spotifygenCLI as spotify_gen_cli # noqa
@pytest.fixture
def mock_env_vars():
    with mock.patch.dict(
        os.environ,
        {
            "SPOTIFY_CLIENT_ID": "test-client-id",
            "SPOTIFY_CLIENT_SECRET": "test-client-secret",
            "SPOTIFY_REDIRECT_URI": "http://localhost:8888/callback",
        },
    ):
        yield


@pytest.fixture
def mock_spotify():
    with mock.patch("spotipy.Spotify") as mock_spotify:
        # Mock the current_user method
        mock_spotify.return_value.current_user.return_value = {"id": "test-user-id"}
        yield mock_spotify.return_value


@pytest.fixture
def mock_spotipy_oauth():
    with mock.patch("spotipy.oauth2.SpotifyOAuth") as mock_oauth:
        yield mock_oauth


@pytest.fixture
def temp_artists_file(tmp_path):
    artists_file = tmp_path / "artists.txt"
    artists_file.write_text("Artist 1\nArtist 2\nArtist 3\n")
    return str(artists_file)


@pytest.fixture
def empty_artists_file(tmp_path):
    artists_file = tmp_path / "empty_artists.txt"
    artists_file.write_text("")
    return str(artists_file)


def test_main_with_missing_env_vars(capsys):
    # Test that the script exits when environment variables are missing
    with mock.patch.dict(os.environ, {}, clear=True):
        with mock.patch("sys.exit") as mock_exit:
            spotify_gen_cli.main()
            mock_exit.assert_called_once_with(1)

    captured = capsys.readouterr()
    assert "Missing required environment variables" in captured.out


def test_main_file_not_found(mock_env_vars, capsys):
    # Test that the script exits when the artists file is not found
    with mock.patch("sys.argv", ["spotify-gen-cli.py", "nonexistent_file.txt"]):
        with mock.patch("sys.exit") as mock_exit:
            spotify_gen_cli.main()
            mock_exit.assert_called_once_with(1)

    captured = capsys.readouterr()
    assert "not found" in captured.out


def test_main_with_empty_file(mock_env_vars, empty_artists_file, capsys):
    # Test that the script exits when the artists file is empty
    with mock.patch("sys.argv", ["spotify-gen-cli.py", empty_artists_file]):
        with mock.patch("sys.exit") as mock_exit:
            spotify_gen_cli.main()
            mock_exit.assert_called_once_with(1)

    captured = capsys.readouterr()
    assert "No artists found" in captured.out


def test_main_authentication_error(mock_env_vars, temp_artists_file, capsys):
    # Test authentication error
    with mock.patch("spotipy.Spotify", side_effect=Exception("Auth error")):
        with mock.patch("sys.argv", ["spotify-gen-cli.py", temp_artists_file]):
            with mock.patch("sys.exit") as mock_exit:
                spotify_gen_cli.main()
                mock_exit.assert_called_once_with(1)

    captured = capsys.readouterr()
    assert "Authentication error" in captured.out


def test_main_successful_execution(
    mock_env_vars, mock_spotify, mock_spotipy_oauth, temp_artists_file, capsys
):
    # Set up the mock responses
    mock_spotify.search.return_value = {
        "artists": {"items": [{"id": "artist1_id", "name": "Artist 1"}]}
    }

    mock_spotify.artist_top_tracks.return_value = {
        "tracks": [{"id": f"top_track_{i}"} for i in range(3)]
    }

    mock_spotify.artist_albums.return_value = {
        "items": [{"id": f"album_{i}", "name": f"Album {i}"} for i in range(3)],
        "next": None,
    }

    mock_spotify.album_tracks.return_value = {
        "items": [{"id": f"track_{i}"} for i in range(5)],
        "next": None,
    }

    mock_spotify.track.return_value = {"id": "track_id", "popularity": 50}

    mock_spotify.user_playlist_create.side_effect = [
        {"id": "popular_playlist_id"},
        {"id": "deep_cuts_playlist_id"},
    ]

    # Run the main function with mocked command line arguments
    with mock.patch("sys.argv", ["spotify-gen-cli.py", temp_artists_file]):
        spotify_gen_cli.main()

    # Verify the expected function calls
    mock_spotify.current_user.assert_called_once()
    mock_spotify.user_playlist_create.assert_called()
    mock_spotify.search.assert_called()
    mock_spotify.artist_top_tracks.assert_called()
    mock_spotify.playlist_add_items.assert_called()

    # Check output
    captured = capsys.readouterr()
    assert "Authenticated as: test-user-id" in captured.out
    assert "Created playlist" in captured.out
    assert "Playlist Creation Summary" in captured.out


def test_main_artist_not_found(
    mock_env_vars, mock_spotify, mock_spotipy_oauth, temp_artists_file, capsys
):
    # Set up the mock to return no artists
    mock_spotify.search.return_value = {"artists": {"items": []}}

    mock_spotify.user_playlist_create.side_effect = [
        {"id": "popular_playlist_id"},
        {"id": "deep_cuts_playlist_id"},
    ]

    # Run the main function
    with mock.patch("sys.argv", ["spotify-gen-cli.py", temp_artists_file]):
        spotify_gen_cli.main()

    # Check that artists were skipped
    captured = capsys.readouterr()
    assert "Could not find artist" in captured.out
    assert "Skipped artists:" in captured.out


def test_main_with_custom_arguments(
    mock_env_vars, mock_spotify, mock_spotipy_oauth, temp_artists_file
):
    # Test with custom command line arguments
    mock_spotify.search.return_value = {
        "artists": {"items": [{"id": "artist1_id", "name": "Artist 1"}]}
    }

    mock_spotify.artist_top_tracks.return_value = {
        "tracks": [{"id": f"top_track_{i}"} for i in range(5)]
    }

    mock_spotify.artist_albums.return_value = {
        "items": [{"id": f"album_{i}", "name": f"Album {i}"} for i in range(3)],
        "next": None,
    }

    mock_spotify.album_tracks.return_value = {
        "items": [{"id": f"track_{i}"} for i in range(5)],
        "next": None,
    }

    mock_spotify.track.return_value = {"id": "track_id", "popularity": 50}

    mock_spotify.user_playlist_create.side_effect = [
        {"id": "popular_playlist_id"},
        {"id": "deep_cuts_playlist_id"},
    ]

    # Run with custom arguments
    with mock.patch(
        "sys.argv",
        [
            "spotify-gen-cli.py",
            temp_artists_file,
            "--popular-limit",
            "5",
            "--deep-limit",
            "4",
            "--country",
            "GB",
            "--popular-name",
            "My Top Tracks",
            "--deep-name",
            "My Deep Cuts",
        ],
    ):
        spotify_gen_cli.main()

    # Verify the custom arguments were used
    mock_spotify.user_playlist_create.assert_any_call(
        "test-user-id", "My Top Tracks", public=True, description=mock.ANY
    )
    mock_spotify.user_playlist_create.assert_any_call(
        "test-user-id", "My Deep Cuts", public=True, description=mock.ANY
    )
    mock_spotify.artist_top_tracks.assert_called_with("artist1_id", "GB")
