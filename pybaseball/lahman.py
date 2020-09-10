import requests
import zipfile
import os
import pandas as pd
from io import BytesIO, StringIO
from bs4 import BeautifulSoup

url = "https://github.com/chadwickbureau/baseballdatabank/archive/master.zip"

def get_base_string(separator):
	return separator.join(["baseballdatabank-master", "core"])

_handle = None
_separator = os.sep
def get_lahman_zip():
    # Retrieve the Lahman database zip file, returns None if file already exists in cwd.
    # If we already have the zip file, keep re-using that.
    # Making this a function since everything else will be re-using these lines
    global _handle, _separator
    if os.path.exists(get_base_string(os.sep)):
        _handle = None
        _separator = os.sep
    elif not _handle:
        s = requests.get(url, stream=True)
        _handle = zipfile.ZipFile(BytesIO(s.content))
        _separator = '/'
    return _handle

def download_lahman():
	# download entire lahman db to present working directory
	z = get_lahman_zip()
	if z is not None:
		z.extractall()
		z = get_lahman_zip()
		# this way we'll now start using the extracted zip directory
		# instead of the session ZipFile object

def parks():
	# do this for every table in the lahman db so they can exist as separate functions
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Parks.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def all_star_full():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "AllstarFull.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def appearances():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Appearances.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def awards_managers():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "AwardsManagers.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def awards_players():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "AwardsPlayers.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def awards_share_managers():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "AwardsShareManagers.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def awards_share_players():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "AwardsSharePlayers.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def batting():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Batting.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def batting_post():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "BattingPost.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def college_playing():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "CollegePlaying.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def fielding():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Fielding.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def fielding_of():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "FieldingOF.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def fielding_of_split():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "FieldingOFsplit.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def fielding_post():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "FieldingPost.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def hall_of_fame():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "HallOfFame.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def home_games():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "HomeGames.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def managers():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Managers.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def managers_half():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "ManagersHalf.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

# Alias for people -- the new name for master
def master():
	return people()

def people():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "People.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def pitching():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Pitching.csv"
	print('FILENAME', f)
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def pitching_post():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "PitchingPost.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def salaries():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Salaries.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def schools():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Schools.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar='"') # different here bc of doublequotes used in some school names
	return data

def series_post():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "SeriesPost.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data 

def teams():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "Teams.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def teams_franchises():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "TeamsFranchises.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

def teams_half():
	z = get_lahman_zip()
	f = get_base_string(_separator) + _separator + "TeamsHalf.csv"
	data = pd.read_csv(f if z is None else z.open(f), header=0, sep=',', quotechar="'")
	return data

