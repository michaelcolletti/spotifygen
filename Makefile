install:
	pip install --upgrade pip &&\
		pip install -r requirements.txt

test:
	#python -m pytest -vvv --cov=read_artists_from_file --cov=find_artist_id \
    # --cov=get_top_tracks --cov=get_deep_cuts  --cov=create_playlist --cov=add_tracks_to_playlist tests
#def read_artists_from_file(file_path):
#def find_artist_id(artist_name):
#def get_top_tracks(artist_id, country='US', limit=3):
#def get_deep_cuts(artist_id, limit=3):
#def create_playlist(name, description):
#def add_tracks_to_playlist(playlist_id, track_ids):

#	python -m pytest --nbval notebook.ipynb	#tests our jupyter notebook
#	python -m pytest -v tests/test_web.py #if you just want to test web
	python -m pytest -vvv tests/test_spotifygen.py tests/test_spotifygenCLI.py 

debug:
	python -m pytest -vv --pdb	#Debugger is invoked

one-test:
	python -m pytest -vv tests/test_greeting.py::test_my_name4

debugthree:
	#not working the way I expect
	python -m pytest -vv --pdb --maxfail=4  # drop to PDB for first three failures

format:
	black src/*.py

lint:
	#pylint --disable=R,C tests/test_spotifygen.py tests/test_spotifygenCLI.py
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics


clean:
		rm -rf __pycache__
		rm -rf .pytest_cache
		rm -rf .coverage
		rm -rf htmlcov
		rm -rf build/
		rm -rf dist/
		rm -rf *.egg-info/

all: install lint test format
