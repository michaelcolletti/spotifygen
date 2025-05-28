import sys
import os
from unittest.mock import patch, mock_open
import pytest

# Add the src directory to path to import the module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import functions directly from the module
from src.spotifygen import (
    read_artists_from_file,
    find_artist_id,
    get_top_tracks,
    get_deep_cuts,
    create_playlist,
    add_tracks_to_playlist
)

class TestSpotifyGen:
    
    @patch('builtins.open', new_callable=mock_open, read_data="Artist 1\nArtist 2\n\nArtist 3")
    def test_read_artists_from_file(self, mock_file):
        # Test reading artists from file
        result = read_artists_from_file("dummy_path.txt")
        mock_file.assert_called_once_with("dummy_path.txt", "r")
        assert result == ["Artist 1", "Artist 2", "Artist 3"]
        assert len(result) == 3
        assert "" not in result  # Empty lines should be filtered

    @patch('spotipy.Spotify')
    def test_find_artist_id_success(self, mock_spotify):
        # Mock a successful artist search
        mock_spotify.search.return_value = {
            'artists': {
                'items': [{'id': '123', 'name': 'Test Artist'}]
            }
        }
        
        with patch('src.spotifygen.sp', mock_spotify):
            artist_id, artist_name = find_artist_id("Test Artist")
        
        mock_spotify.search.assert_called_once_with(q="artist:Test Artist", type="artist", limit=1)
        assert artist_id == '123'
        assert artist_name == 'Test Artist'

    @patch('spotipy.Spotify')
    def test_find_artist_id_not_found(self, mock_spotify):
        # Mock an unsuccessful artist search
        mock_spotify.search.return_value = {'artists': {'items': []}}
        
        with patch('src.spotifygen.sp', mock_spotify):
            artist_id, artist_name = find_artist_id("Nonexistent Artist")
        
        assert artist_id is None
        assert artist_name is None

    @patch('spotipy.Spotify')
    def test_get_top_tracks(self, mock_spotify):
        # Mock top tracks response
        mock_spotify.artist_top_tracks.return_value = {
            'tracks': [
                {'id': 'track1', 'name': 'Top Track 1'},
                {'id': 'track2', 'name': 'Top Track 2'},
                {'id': 'track3', 'name': 'Top Track 3'},
                {'id': 'track4', 'name': 'Top Track 4'}
            ]
        }
        
        with patch('src.spotifygen.sp', mock_spotify):
            result = get_top_tracks('artist123', limit=3)
        
        mock_spotify.artist_top_tracks.assert_called_once_with('artist123', 'US')
        assert len(result) == 3  # Should respect limit parameter
        assert result[0]['id'] == 'track1'

    @patch('spotipy.Spotify')
    @patch('time.sleep')  # Mock sleep to speed up tests
    def test_get_deep_cuts(self, mock_sleep, mock_spotify):
        # Mock albums response
        mock_spotify.artist_albums.return_value = {
            'items': [
                {'id': 'album1', 'name': 'Album One'},
                {'id': 'album2', 'name': 'Album Two'}
            ],
            'next': None
        }
        
        # Mock album tracks
        mock_spotify.album_tracks.return_value = {
            'items': [{'id': 'track1'}, {'id': 'track2'}],
            'next': None
        }
        
        # Mock full track info
        mock_spotify.track.side_effect = [
            {'id': 'track1', 'popularity': 30},
            {'id': 'track2', 'popularity': 10}
        ]
        
        with patch('src.spotifygen.sp', mock_spotify):
            result = get_deep_cuts('artist123', limit=2)
        
        assert len(result) == 2
        # Tracks should be sorted by popularity (ascending)
        assert result[0]['popularity'] == 10
        assert result[1]['popularity'] == 30

    @patch('spotipy.Spotify')
    def test_create_playlist(self, mock_spotify):
        # Mock create playlist response
        mock_spotify.user_playlist_create.return_value = {'id': 'playlist123'}
        
        with patch('src.spotifygen.sp', mock_spotify):
            with patch('src.spotifygen.user_id', 'test_user'):
                result = create_playlist("Test Playlist", "Test Description")
        
        mock_spotify.user_playlist_create.assert_called_once_with(
            'test_user', "Test Playlist", public=True, description="Test Description"
        )
        assert result == 'playlist123'

    @patch('spotipy.Spotify')
    def test_add_tracks_to_playlist(self, mock_spotify):
        # Test adding tracks with batching
        with patch('src.spotifygen.sp', mock_spotify):
            # Create a list of more than 100 track IDs to test batching
            track_ids = [f'track{i}' for i in range(150)]
            
            add_tracks_to_playlist('playlist123', track_ids)
        
        # Should have called playlist_add_items twice: once with 100 tracks, once with 50
        assert mock_spotify.playlist_add_items.call_count == 2
        
        # Check first call with first 100 tracks
        first_call_args = mock_spotify.playlist_add_items.call_args_list[0][0]
        assert first_call_args[0] == 'playlist123'
        assert len(first_call_args[1]) == 100
        assert first_call_args[1][0] == 'track0'
        
        # Check second call with remaining 50 tracks
        second_call_args = mock_spotify.playlist_add_items.call_args_list[1][0]
        assert second_call_args[0] == 'playlist123'
        assert len(second_call_args[1]) == 50
        assert second_call_args[1][0] == 'track100'
