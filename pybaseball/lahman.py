from io import BytesIO
from os import path
from typing import Optional
from zipfile import ZipFile

import pandas as pd
import requests

from . import cache

url = "https://github.com/chadwickbureau/baseballdatabank/archive/master.zip"
base_string = "baseballdatabank-master"

_handle = None

def get_lahman_zip() -> Optional[ZipFile]:
    # Retrieve the Lahman database zip file, returns None if file already exists in cwd.
    # If we already have the zip file, keep re-using that.
    # Making this a function since everything else will be re-using these lines
    global _handle
    if path.exists(path.join(cache.config.cache_directory, base_string)):
        _handle = None
    elif not _handle:
        s = requests.get(url, stream=True)
        _handle = ZipFile(BytesIO(s.content))
    return _handle

def download_lahman():
    # download entire lahman db to present working directory
    z = get_lahman_zip()
    if z is not None:
        z.extractall(cache.config.cache_directory)
        z = get_lahman_zip()
        # this way we'll now start using the extracted zip directory
        # instead of the session ZipFile object

def _get_file(tablename: str, quotechar: str = "'") -> pd.DataFrame:
    z = get_lahman_zip()
    f = f'{base_string}/{tablename}'
    data = pd.read_csv(
        f"{path.join(cache.config.cache_directory, f)}" if z is None else z.open(f),
        header=0,
        sep=',',
        quotechar=quotechar
    )
    return data


# do this for every table in the lahman db so they can exist as separate functions
def parks() -> pd.DataFrame:
    return _get_file('core/Parks.csv')

def all_star_full() -> pd.DataFrame:
    return _get_file("core/AllstarFull.csv")

def appearances() -> pd.DataFrame:
    return _get_file("core/Appearances.csv")

def awards_managers() -> pd.DataFrame:
    return _get_file("contrib/AwardsManagers.csv")

def awards_players() -> pd.DataFrame:
    return _get_file("contrib/AwardsPlayers.csv")

def awards_share_managers() -> pd.DataFrame:
    return _get_file("contrib/AwardsShareManagers.csv")

def awards_share_players() -> pd.DataFrame:
    return _get_file("contrib/AwardsSharePlayers.csv")

def batting() -> pd.DataFrame:
    return _get_file("core/Batting.csv")

def batting_post() -> pd.DataFrame:
    return _get_file("core/BattingPost.csv")

def college_playing() -> pd.DataFrame:
    return _get_file("contrib/CollegePlaying.csv")

def fielding() -> pd.DataFrame:
    return _get_file("core/Fielding.csv")

def fielding_of() -> pd.DataFrame:
    return _get_file("core/FieldingOF.csv")

def fielding_of_split() -> pd.DataFrame:
    return _get_file("core/FieldingOFsplit.csv")

def fielding_post() -> pd.DataFrame:
    return _get_file("core/FieldingPost.csv")

def hall_of_fame() -> pd.DataFrame:
    return _get_file("contrib/HallOfFame.csv")

def home_games() -> pd.DataFrame:
    return _get_file("core/HomeGames.csv")

def managers() -> pd.DataFrame:
    return _get_file("core/Managers.csv")

def managers_half() -> pd.DataFrame:
    return _get_file("core/ManagersHalf.csv")

def master() -> pd.DataFrame:
    # Alias for people -- the new name for master
    return people()

def people() -> pd.DataFrame:
    return _get_file("core/People.csv")

def pitching() -> pd.DataFrame:
    return _get_file("core/Pitching.csv")

def pitching_post() -> pd.DataFrame:
    return _get_file("core/PitchingPost.csv")

def salaries() -> pd.DataFrame:
    return _get_file("contrib/Salaries.csv")

def schools() -> pd.DataFrame:
    return _get_file("contrib/Schools.csv", quotechar='"')  # different here bc of doublequotes used in some school names

def series_post() -> pd.DataFrame:
    return _get_file("core/SeriesPost.csv")

def teams_core() -> pd.DataFrame:
    return _get_file("core/Teams.csv")

def teams_upstream() -> pd.DataFrame:
    return _get_file("upstream/Teams.csv") # manually maintained file

def teams_franchises() -> pd.DataFrame:
    return _get_file("core/TeamsFranchises.csv")

def teams_half() -> pd.DataFrame:
    return _get_file("core/TeamsHalf.csv")
