from io import StringIO
from os import path
from typing import Optional
import py7zr
import pandas as pd
import requests

from . import cache

url = "https://www.dropbox.com/scl/fi/hy0sxw6gaai7ghemrshi8/lahman_1871-2023_csv.7z?rlkey=edw1u63zzxg48gvpcmr3qpnhz&e=1&dl=1"
base_string = "lahman_1871-2023_csv"

_handle = None


def get_lahman_7z() -> Optional[str]:

    global _handle
    if path.exists(path.join(cache.config.cache_directory, base_string)):
        _handle = None
    elif not _handle:
        response = requests.get(url, stream=True)
        local_7z = path.join(cache.config.cache_directory, "lahman_1871-2023_csv.7z")
        with open(local_7z, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        _handle = local_7z
    return _handle


def download_lahman():
    # download entire lahman db to present working directory
    z = get_lahman_7z()
    if z is not None:
        with py7zr.SevenZipFile(z, mode="r") as archive:
            archive.extractall(path=cache.config.cache_directory)


def _get_file(
    tablename: str, quotechar: str = "'", encoding: str = "latin1"
) -> pd.DataFrame:
    z = get_lahman_7z()
    f = f"{base_string}/{tablename}"
    if z is not None:
        download_lahman()
    data = pd.read_csv(
        f"{path.join(cache.config.cache_directory, f)}",
        header=0,
        sep=",",
        quotechar=quotechar,
        encoding=encoding,
    )
    return data


# do this for every table in the lahman db so they can exist as separate functions
def parks() -> pd.DataFrame:
    return _get_file("Parks.csv")


def all_star_full() -> pd.DataFrame:
    return _get_file("AllstarFull.csv")


def appearances() -> pd.DataFrame:
    return _get_file("Appearances.csv")


def awards_managers() -> pd.DataFrame:
    return _get_file("AwardsManagers.csv")


def awards_players() -> pd.DataFrame:
    return _get_file("AwardsPlayers.csv")


def awards_share_managers() -> pd.DataFrame:
    return _get_file("AwardsShareManagers.csv")


def awards_share_players() -> pd.DataFrame:
    return _get_file("AwardsSharePlayers.csv")


def batting() -> pd.DataFrame:
    return _get_file("Batting.csv")


def batting_post() -> pd.DataFrame:
    return _get_file("BattingPost.csv")


def college_playing() -> pd.DataFrame:
    return _get_file("CollegePlaying.csv")


def fielding() -> pd.DataFrame:
    return _get_file("Fielding.csv")


def fielding_of() -> pd.DataFrame:
    return _get_file("FieldingOF.csv")


def fielding_of_split() -> pd.DataFrame:
    return _get_file("FieldingOFsplit.csv")


def fielding_post() -> pd.DataFrame:
    return _get_file("FieldingPost.csv")


def hall_of_fame() -> pd.DataFrame:
    return _get_file("HallOfFame.csv")


def home_games() -> pd.DataFrame:
    return _get_file("HomeGames.csv")


def managers() -> pd.DataFrame:
    return _get_file("Managers.csv")


def managers_half() -> pd.DataFrame:
    return _get_file("ManagersHalf.csv")


def master() -> pd.DataFrame:
    # Alias for people -- the new name for master
    return people()


def people() -> pd.DataFrame:
    return _get_file("People.csv")


def pitching() -> pd.DataFrame:
    return _get_file("Pitching.csv")


def pitching_post() -> pd.DataFrame:
    return _get_file("PitchingPost.csv")


def salaries() -> pd.DataFrame:
    return _get_file("Salaries.csv")


def series_post() -> pd.DataFrame:
    return _get_file("SeriesPost.csv")


def teams_core() -> pd.DataFrame:
    return _get_file("Teams.csv")


# def teams_upstream() -> pd.DataFrame:
#     return _get_file("upstream/Teams.csv") # manually maintained file


def teams_franchises() -> pd.DataFrame:
    return _get_file("TeamsFranchises.csv")


def teams_half() -> pd.DataFrame:
    return _get_file("TeamsHalf.csv")


def schools() -> pd.DataFrame:
    """Clean up the schools to allows pandas reading"""
    f = f"{base_string}/Schools.csv"
    file = f"{path.join(cache.config.cache_directory, f)}"
    if not path.exists(file):
        download_lahman()
    with open(file, "r") as f:
        csv_data = f.read()
    csv_data = csv_data.replace(", ", " ")
    return pd.read_csv(
        StringIO(csv_data), header=0, sep=",", quotechar='"', encoding="latin1"
    )
