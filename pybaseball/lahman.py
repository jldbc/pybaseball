from datetime import timedelta
from io import BytesIO
from os import makedirs
from os import path

from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from py7zr import SevenZipFile
import requests
from requests_cache import CachedSession

from . import cache

# For example, "https://www.dropbox.com/scl/fi/hy0sxw6gaai7ghemrshi8/lahman_1871-2023_csv.7z?rlkey=edw1u63zzxg48gvpcmr3qpnhz&dl=1"
def _get_download_url() -> str:
    session = _get_session()
    response = session.get("http://seanlahman.com")
    soup = BeautifulSoup(response.content, "html.parser")

    anchor = soup.find("a", string="Comma-delimited version")
    url = anchor["href"].replace("dl=0", "dl=1")

    return url

def _get_cache_dir() -> str:
    return f"{cache.config.cache_directory}/lahman"

def _get_session() -> CachedSession:
    return CachedSession(_get_cache_dir(), expire_after=timedelta(days=30))

def _get_base_string() -> str:
    url = _get_download_url()
    path = Path(url)

    return path.stem

def _get_file_path(filename: str = "") -> str:
    base_string = _get_base_string()
    return path.join(_get_cache_dir(), base_string, filename)

def _get_table(filename: str,
               quotechar: str = "'",
               encoding=None,
               on_bad_lines="error") -> pd.DataFrame:
    filepath = _get_file_path(filename)
    data = pd.read_csv(
        filepath,
        header=0,
        sep=",",
        quotechar=quotechar,
        encoding=encoding,
        on_bad_lines=on_bad_lines,
    )
    return data

def download_lahman(force: bool = False) -> bool:
    if force or not path.exists(_get_file_path()):
        cache_dir = _get_cache_dir()
        base_string = _get_base_string()
        makedirs(f"{cache_dir}/{base_string}", exist_ok=True)

        url = _get_download_url()
        stream = requests.get(url, stream=True)
        with SevenZipFile(BytesIO(stream.content)) as zip:
            zip.extractall(cache_dir)
        return True
    return False

# do this for every table in the lahman db so they can exist as separate functions
def all_star_full() -> pd.DataFrame:
    return _get_table("AllstarFull.csv")

def appearances() -> pd.DataFrame:
    return _get_table("Appearances.csv")

def awards_managers() -> pd.DataFrame:
    return _get_table("AwardsManagers.csv")

def awards_players() -> pd.DataFrame:
    return _get_table("AwardsPlayers.csv")

def awards_share_managers() -> pd.DataFrame:
    return _get_table("AwardsShareManagers.csv")

def awards_share_players() -> pd.DataFrame:
    return _get_table("AwardsSharePlayers.csv")

def batting() -> pd.DataFrame:
    return _get_table("Batting.csv")

def batting_post() -> pd.DataFrame:
    return _get_table("BattingPost.csv")

def college_playing() -> pd.DataFrame:
    return _get_table("CollegePlaying.csv")

def fielding() -> pd.DataFrame:
    return _get_table("Fielding.csv")

def fielding_of() -> pd.DataFrame:
    return _get_table("FieldingOF.csv")

def fielding_of_split() -> pd.DataFrame:
    return _get_table("FieldingOFsplit.csv")

def fielding_post() -> pd.DataFrame:
    return _get_table("FieldingPost.csv")

def hall_of_fame() -> pd.DataFrame:
    return _get_table("HallOfFame.csv")

def home_games() -> pd.DataFrame:
    return _get_table("HomeGames.csv")

def managers() -> pd.DataFrame:
    return _get_table("Managers.csv")

def managers_half() -> pd.DataFrame:
    return _get_table("ManagersHalf.csv")

def master() -> pd.DataFrame:
    # Alias for people -- the new name for master
    return people()

def parks() -> pd.DataFrame:
    return _get_table("Parks.csv", encoding="unicode_escape")

def people() -> pd.DataFrame:
    return _get_table("People.csv", encoding="unicode_escape")

def pitching() -> pd.DataFrame:
    return _get_table("Pitching.csv")

def pitching_post() -> pd.DataFrame:
    return _get_table("PitchingPost.csv")

def salaries() -> pd.DataFrame:
    return _get_table("Salaries.csv")

def schools() -> pd.DataFrame:
    # NB: one line is bad; "brklyncuny" should use double quotes, but doesn't
    return _get_table("Schools.csv", quotechar='"', on_bad_lines="skip")

def series_post() -> pd.DataFrame:
    return _get_table("SeriesPost.csv")

def teams_core() -> pd.DataFrame:
    return _get_table("Teams.csv")

def teams_franchises() -> pd.DataFrame:
    return _get_table("TeamsFranchises.csv")

def teams_half() -> pd.DataFrame:
    return _get_table("TeamsHalf.csv")
