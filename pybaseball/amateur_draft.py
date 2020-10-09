import pandas as pd
import requests

from . import cache

# pylint: disable=line-too-long
_URL = "https://www.baseball-reference.com/draft/?year_ID={year}&draft_round={draft_round}&draft_type=junreg&query_type=year_round&"


def get_draft_results(year: int, draft_round: int) -> pd.DataFrame:
    url = _URL.format(year=year, draft_round=draft_round)
    res = requests.get(url, timeout=None).content
    draft_results = pd.read_html(res)
    return draft_results


@cache.df_cache()
def amateur_draft(year: int, draft_round: int, keep_stats: bool = True) -> pd.DataFrame:
    draft_results = get_draft_results(year, draft_round)
    draft_results = pd.concat(draft_results)
    draft_results = postprocess(draft_results)
    if not keep_stats:
        draft_results = drop_stats(draft_results)
    return draft_results


def postprocess(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results = draft_results.drop(['Year', 'Rnd', 'RdPck', 'DT', 'FrRnd'], axis=1)
    return remove_name_suffix(draft_results)


def drop_stats(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results.drop(['WAR', 'G', 'AB', 'HR', 'BA', 'OPS', 'G.1', 'W', 'L', 'ERA', 'WHIP', 'SV'], axis=1,
                       inplace=True)
    return draft_results


def remove_name_suffix(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results.loc[:, 'Name'] = draft_results['Name'].apply(remove_minors_link)
    return draft_results


def remove_minors_link(draftee: str) -> str:
    return draftee.split('(')[0]
