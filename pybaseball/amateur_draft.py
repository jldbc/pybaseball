import pandas as pd
import requests

def get_draft_results(year, round): 
    url = f"https://www.baseball-reference.com/draft/?year_ID={year}&draft_round={round}&draft_type=junreg&query_type=year_round&"
    res = requests.get(url, timeout=None).content 
    draft_results = pd.read_html(res)
    return draft_results

def amateur_draft(year, round, keep_stats=True):
    draft_results = get_draft_results(year, round)
    draft_results = pd.concat(draft_results)
    draft_results = postprocess(draft_results)
    if (not(keep_stats)):
        draft_results = drop_stats(draft_results)
    return draft_results

def postprocess(draft_results):
    draft_results = draft_results.drop(['Year', 'Rnd', 'RdPck', 'DT', 'FrRnd'], axis=1)
    return remove_name_suffix(draft_results)

def drop_stats(draft_results):
    draft_results.drop(['WAR', 'G', 'AB', 'HR', 'BA', 'OPS', 'G.1', 'W', 'L', 'ERA', 'WHIP', 'SV'], axis=1, inplace=True)
    return draft_results

def remove_name_suffix(draft_results):
    draft_results.loc[:,'Name'] = draft_results['Name'].apply(remove_minors_link)
    return draft_results

def remove_minors_link(draftee):
    return draftee.split('(')[0]
