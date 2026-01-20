import json

import pandas as pd
import requests
from bs4 import BeautifulSoup

from pybaseball.teamid_lookup import fg_team_id_dict

from . import cache

# pylint: disable=line-too-long
_URL = "https://www.fangraphs.com/projections?pos={pos}&stats={stats}&type={proj_source}&team={team}&lg={lg}"


@cache.df_cache()
def fg_projections(proj_source: str = "zips", position: str = "batters", league: str = "mlb", team: str = "") -> pd.DataFrame:
    """Retrieves player projection statistics from Fangraphs. View markdown documentation for complete list of valid arguments.

    Args:
        proj_source (str, optional): Projection source, including pre-season, rest of season, updated in-season, 3 year, and on pace leader options. Defaults to "zips".
        position (str, optional): Batters/Pitchers, field position, or pitcher type. Defaults to "batters".
        league (str, optional): mlb, al, or nl. Defaults to "mlb".
        team (str, optional): filter to a specific team by team abbreviation (i.e. for the Philadelphia Phillies, use `PHI`). Defaults to empty (all teams)

    Returns:
        pd.DataFrame: Projections data set given applied filters, columns vary for batters versus pitcher. Returns empty dataframe when no data found on Fangraphs
    """
    args = _FgProjectionArgument(position, proj_source, league, team)
    source = requests.get(args.url, timeout=None)

    soup = BeautifulSoup(source.content, 'html.parser')
    raw = soup.find('script', id='__NEXT_DATA__', type='application/json').string
    data = json.loads(raw)['props']['pageProps']['dehydratedState']['queries'][0]['state']['data']
    result = pd.read_json(json.dumps(data))

    if result.empty:
        return pd.DataFrame()

    # drop last curiously empty column
    result = result.drop(columns=['.'])
    return _transform_name_to_url(result)


def _transform_name_to_url(df: pd.DataFrame) -> pd.DataFrame:
    df['Name'] = df['Name'].str.extract(r'(statss.aspx\?playerid=[\d\w]+&position=[A-Z1-9/]+)', expand=False)
    return df.rename({'Name': 'URL'}, axis='columns')


class _FgProjectionArgument:
    stats: str
    position: str
    proj_source: str
    league: str
    team_id: int
    url: str

    _error_message = "{value} is not a valid {var} argument"

    _position_options = ["batters", "pitchers", "c", "1b", "2b", "3b", "ss", "lf", "cf", "rf", "of", "dh", "sp", "rp"]
    _proj_source_options = ["zips", "zipsdc", "steamer", "fangraphsdc", "atc", "thebat", "thebatx", "rzips", "steamerr",
                            "rfangraphsdc", "rthebat", "rthebatx", "uzips", "steameru", "steamer600", "zipsp1", "zipsp2", "onpaceegp", "onpacegpp"]
    _league_options = ["mlb", "al", "nl"]

    def __init__(self, position: str, proj_source: str, league: str, team: str):
        self.position = position.lower()
        self.proj_source = proj_source.lower()
        self.league = league.lower()
        self.team_id = self._lookup_team_id(team)
        self._validate_arguments()
        self.url = self._generate_url()

    def _lookup_team_id(self, team: str) -> int:
        if team is None or team == "":
            return 0

        fg_team_id = fg_team_id_dict().get(team)
        if fg_team_id is None:
            raise ValueError(self._error_message.format(value=team, var="team"))

        return fg_team_id

    def _is_pitchers(self) -> bool:
        return self.position in ["pitchers", "sp", "rp"]

    def _is_all_pos(self) -> bool:
        return self.position in ["batters", "pitchers"]

    def _validate_arguments(self) -> None:
        if self.position not in self._position_options:
            raise ValueError(self._error_message.format(value=self.position, var="position"))

        elif self.proj_source not in self._proj_source_options:
            raise ValueError(self._error_message.format(value=self.proj_source, var="proj_source"))

        elif self.league not in self._league_options:
            raise ValueError(self._error_message.format(value=self.league, var="league"))

    def _generate_url(self) -> str:
        pos_arg = ""
        stats_arg = ""
        league_arg = "" if self.league == "mlb" else self.league
        team_arg = "" if self.team_id == 0 else self.team_id

        if self._is_pitchers():
            if self._is_all_pos():
                stats_arg = "pit"
            elif self.position == "rp":
                stats_arg = "rel"
            elif self.position == "sp":
                stats_arg = "sta"
        else:
            stats_arg = "bat"
            if not self._is_all_pos():
                pos_arg = self.position

        return _URL.format(pos=pos_arg, stats=stats_arg, proj_source=self.proj_source, team=team_arg, lg=league_arg)
