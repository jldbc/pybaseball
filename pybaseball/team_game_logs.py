import pandas as pd
import requests
from bs4 import BeautifulSoup

from . import cache

_URL = "https://www.baseball-reference.com/teams/tgl.cgi?team={}&t={}&year={}"


def get_table(season, team, log_type):
    t_param = "b" if log_type == "batting" else "p"
    content = requests.get(_URL.format(team, t_param, season)).content
    soup = BeautifulSoup(content, "lxml")
    table_id = "team_{}_gamelogs".format(log_type)
    table = soup.find("table", attrs=dict(id=table_id))
    if table is None:
        raise RuntimeError("Table with expected id not found on scraped page.")
    data = pd.read_html(str(table))[0]
    return data


def postprocess(data):
    data.drop("Rk", axis=1, inplace=True)  # drop index column
    repl_dict = {
        "Gtm": "Game",
        "Unnamed: 3": "Home",
        "#": "NumPlayers",
        "Opp. Starter (GmeSc)": "OppStart",
        "Pitchers Used (Rest-GameScore-Dec)": "PitchersUsed"
    }
    data.rename(repl_dict, axis=1, inplace=True)
    data["Home"] = ~data["Home"].isnull()  # '@' if away, empty if home
    data = data[data["Game"].str.match(r"\d+")]  # drop empty month rows
    data = data.apply(pd.to_numeric, errors="ignore")
    data["Game"] = data["Game"].astype(int)
    return data.reset_index(drop=True)


@cache.df_cache()
def team_game_logs(season, team, log_type="batting"):
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
