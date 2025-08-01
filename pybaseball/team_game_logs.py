import pandas as pd
from bs4 import BeautifulSoup
from io import StringIO

from . import cache
from .datasources.bref import BRefSession

session = BRefSession()

_URL = "https://www.baseball-reference.com/teams/tgl.cgi?team={}&t={}&year={}"


def get_table(season: int, team: str, log_type: str) -> pd.DataFrame:
    t_param = "b" if log_type == "batting" else "p"
    content = session.get(_URL.format(team, t_param, season)).content
    soup = BeautifulSoup(content, "lxml")
    table_id = "players_standard_{}".format(log_type)
    table = soup.find("table", attrs=dict(id=table_id))
    if table is None:
        raise RuntimeError("Table with expected id not found on scraped page.")
    data = pd.read_html(StringIO(str(table)))[0]
    return data


def postprocess(data: pd.DataFrame) -> pd.DataFrame:
    #print(data.columns)
    data.drop([('Unnamed: 0_level_0', 'Rk')], axis=1, inplace=True)  # drop index column
    data = data.iloc[:-1]
    repl_dict = {
        "Gtm" : "Game",
        "Unnamed: 3_level_1": "Home",
        "#": "NumPlayers",
        "Opp. Starter (GmeSc)": "OppStart",
        "Pitchers Used (Rest-GameScore-Dec)": "PitchersUsed"
    }
    data = data.rename(columns= repl_dict).copy()
    data[('Unnamed: 3_level_0','Home')] = data[('Unnamed: 3_level_0','Home')].isnull()  # '@' if away, empty if home
    data = data[data[('Unnamed: 1_level_0','Game')] != 'Gtm'].copy()  # drop empty month rows
    data = data.apply(pd.to_numeric, errors="ignore")
    data[('Unnamed: 1_level_0','Game')] = data[('Unnamed: 1_level_0','Game')].astype(int)
    return data.reset_index(drop=True)


@cache.df_cache()
def team_game_logs(season: int, team: str, log_type: str="batting") -> pd.DataFrame:
    """
    Get Baseball Reference batting or pitching game logs for a team-season.

    :param season: year of logs
    :param team: team abbreviation
    :param log_type: "batting" (default) or "pitching"
    :return: pandas.DataFrame of game logs
    """
    if log_type not in ("batting", "pitching"):
        raise ValueError("`log_type` must be either 'batting' or 'pitching'.")
    data = get_table(season, team, log_type)
    data = postprocess(data)
    return data
