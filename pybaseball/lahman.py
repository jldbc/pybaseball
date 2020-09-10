import os
import zipfile
from io import BytesIO
from typing import Optional, Union, Tuple, IO

import pandas as pd
import requests

_lahman_url = "https://github.com/chadwickbureau/baseballdatabank/archive/master.zip"

def get_base_string(separator: str = os.sep) -> str:
    return separator.join(["baseballdatabank-master", "core"])

def get_file_name(separator: str, filename: str) -> str:
    return separator.join([get_base_string(separator), filename])


def _read_lahman_data_file(filename: str, header: int = 0, sep: str = ',', quotechar: str = "'") -> pd.DataFrame:
    (z, separator) = get_lahman_zip()
    filepath = get_file_name(separator, filename)
    _file_handle: Optional[Union[str, IO[bytes]]] = None
    if z is not None:
        _file_handle = z.open(filepath)
    elif not os.path.exists(filepath):
        # If we have the files locally, but ours is missing, then use the remote
        (z, separator) = get_lahman_zip(force_remote=True)
        filepath = get_file_name(separator, filename)
        # We should have a handle now, else fail
        assert z is not None
        _file_handle = z.open(filepath)
    else:
        _file_handle = filepath

    return pd.read_csv(_file_handle, header=header, sep=sep, quotechar=quotechar)

def get_lahman_zip(force_remote: bool = False) -> Tuple[Optional[zipfile.ZipFile], str]:
    # Retrieve the Lahman database zip file, returns None if file already exists in cwd.
    # If we already have the zip file, keep re-using that.
    # Making this a function since everything else will be re-using these lines
    if os.path.exists(get_base_string()) and not force_remote:
        handle = None
        separator = os.sep
    else:
        s = requests.get(_lahman_url, stream=True)
        handle = zipfile.ZipFile(BytesIO(s.content))
        separator = '/' # File separator inside the zip is always / regardless of os
    return (handle, separator)

def download_lahman() -> Tuple[Optional[zipfile.ZipFile], str]:
    # Download entire lahman db to present working directory
    (z, separator) = get_lahman_zip()
    if z is not None:
        z.extractall()
        return get_lahman_zip()
    return (z, separator)

def parks() -> pd.DataFrame:
    return _read_lahman_data_file("Parks.csv")

def all_star_full():
    return _read_lahman_data_file("AllstarFull.csv")

def appearances():
    return _read_lahman_data_file("Appearances.csv")

def awards_managers():
    return _read_lahman_data_file("AwardsManagers.csv")

def awards_players():
    return _read_lahman_data_file("AwardsPlayers.csv")

def awards_share_managers():
    return _read_lahman_data_file("AwardsShareManagers.csv")

def awards_share_players():
    return _read_lahman_data_file("AwardsSharePlayers.csv")

def batting():
    return _read_lahman_data_file("Batting.csv")

def batting_post():
    return _read_lahman_data_file("BattingPost.csv")

def college_playing():
    return _read_lahman_data_file("CollegePlaying.csv")

def fielding():
    return _read_lahman_data_file("Fielding.csv")

def fielding_of():
    return _read_lahman_data_file("FieldingOF.csv")

def fielding_of_split():
    return _read_lahman_data_file("FieldingOFsplit.csv")

def fielding_post():
    return _read_lahman_data_file("FieldingPost.csv")

def hall_of_fame():
    return _read_lahman_data_file("HallOfFame.csv")

def home_games():
    return _read_lahman_data_file("HomeGames.csv")

def managers():
    return _read_lahman_data_file("Managers.csv")

def managers_half():
    return _read_lahman_data_file("ManagersHalf.csv")

# Alias for people -- the new name for master
def master():
    return people()

def people():
    return _read_lahman_data_file("People.csv")

def pitching():
    return _read_lahman_data_file("Pitching.csv")

def pitching_post():
    return _read_lahman_data_file("PitchingPost.csv")

def salaries():
    return _read_lahman_data_file("Salaries.csv")

def schools():
    # Different quotechar here bc of doublequotes used in some school names
    return _read_lahman_data_file("Schools.csv", quotechar='"')

def series_post():
    return _read_lahman_data_file("SeriesPost.csv")

def teams():
    return _read_lahman_data_file("Teams.csv")

def teams_franchises():
    return _read_lahman_data_file("TeamsFranchises.csv")

def teams_half():
    return _read_lahman_data_file("TeamsHalf.csv")
