import pandas as pd

from . import cache
from .datasources.bref import BRefSession

session = BRefSession()

# pylint: disable=line-too-long
_URL = "https://www.baseball-reference.com/draft/?team_ID={team}&year_ID={year}&draft_type=junreg&query_type=franch_year"


def get_draft_results(team: str, year: int) -> pd.DataFrame:
    url = _URL.format(team=team, year=year)
    res = session.get(url, timeout=None).content
    draft_results = pd.read_html(res)
    return pd.concat(draft_results)


def postprocess(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results = draft_results.drop(["Year", "Rnd", "RdPck", "DT"], axis=1)
    return remove_name_suffix(draft_results)


def remove_name_suffix(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results.loc[:, "Name"] = draft_results["Name"].apply(remove_minors_link)
    return draft_results


def remove_minors_link(draftee: str) -> str:
    return draftee.split("(")[0]


def drop_stats(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results.drop(
        ["WAR", "G", "AB", "HR", "BA", "OPS", "G.1", "W", "L", "ERA", "WHIP", "SV"],
        axis=1,
        inplace=True,
    )
    return draft_results


@cache.df_cache()
def amateur_draft_by_team(
    team: str, year: int, keep_stats: bool = True
) -> pd.DataFrame:
    """
    Get amateur draft results by team and year.

    ARGUMENTS
        team: Team code which you want to check. See docs for team codes 
            (https://github.com/jldbc/pybaseball/blob/master/docs/amateur_draft_by_team.md)
        year: Year which you want to check.

    """
    draft_results = get_draft_results(team, year)
    draft_results = postprocess(draft_results)
    if not keep_stats:
        draft_results = drop_stats(draft_results)
    return draft_results
