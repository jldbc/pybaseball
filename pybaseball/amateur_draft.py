import pandas as pd

from . import cache
from .datasources.bref import BRefSession

session = BRefSession()

# pylint: disable=line-too-long
_URL = "https://www.baseball-reference.com/draft/?year_ID={year}&draft_round={draft_round}&draft_type=junreg&query_type=year_round&"


def get_draft_results(year: int, draft_round: int, include_id: bool) -> pd.DataFrame:
    url = _URL.format(year=year, draft_round=draft_round)
    res = session.get(url, timeout=None).content
    extract_links = 'body' if include_id else None
    draft_results = pd.read_html(res, extract_links=extract_links)
    draft_results = pd.concat(draft_results)
    if include_id:
        draft_results = clean_draft_results_with_links(draft_results)
    return draft_results

def clean_draft_results_with_links(draft_results: pd.DataFrame) -> pd.DataFrame:
    draft_results['link'] = draft_results['Name'].apply(
        lambda value: value[1] if value[1] != None else 'NA'
        )
    draft_results['id_type'] = draft_results['link'].apply(
        lambda value:
            'baseball_reference_minor_league_id' if 'register' in value 
            else 'baseball_reference_id' if 'players' in value
            else 'NA'
        )
    draft_results['player_id'] = draft_results['link'].apply(
        lambda value:
            value.split('=')[-1] if 'register' in value 
            else value.split('/')[-1].split('.')[0] if 'players' in value
            else 'NA'
        )
    draft_results['notes'] = draft_results['Name'].apply(
        lambda value: value[0].split('(')[1].split(')')[0] if value[1] == None else 'NA'
        )
    draft_results['team_id'] = draft_results['Tm'].apply(
        lambda value: value[1].split('team_ID=')[-1].split('&year_ID=')[0] if value[1] != None else 'NA'
    )
    draft_results = draft_results.apply(
        lambda column: [
            value[0] if column.name not in ['link', 'id_type', 'player_id', 'notes', 'team_id'] 
            else value for value in column
            ]
        )
    return draft_results

@cache.df_cache()
def amateur_draft(year: int, draft_round: int, include_id: bool = False, keep_stats: bool = True, keep_columns: bool = False) -> pd.DataFrame:
    """
    Retrieves the MLB amateur draft results by year and round.

    ARGUMENTS
        year: The year for which you wish to retrieve draft results.
        draft_round: The round for which you wish to retrieve draft results. There is no distinction made 
            between the competitive balance, supplementary, and main portions of a round.
        include_id: A boolean parameter that controls whether the 'player_id' column is included in the
            returned DataFrame. Default set to false.
        keep_stats: A boolean parameter that controls whether the major league stats of each draftee is 
            displayed. Default set to true.
        keep_columns: A boolean parameter that controls whether the columns 'Year', 'Rnd', 'RdPck', 'DT',
            'FrRnd' are returned. Default set to false.
    """
    draft_results = get_draft_results(year, draft_round, include_id)
    if not keep_columns:
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
