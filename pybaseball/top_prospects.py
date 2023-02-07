import pandas as pd
import requests
import json
from datetime import date

from . import cache


@cache.df_cache()
def top_prospects(teamName=None, playerType=None,
                  fg=False, year=date.today().year):
    """
    A function to return a dataframe with a list of top prospects given a set of params

    Parameters
    ----------
    teamName : str, optional
        For FG: this is the 3 letter UPPER abbreviation: BAL = Baltimore Orioles, etc.
        For MLB: Legacy code has been updated as MLB has converted all "named" lilnks to ids
        The default is None.
    playerType : str, optional
        The type of player desired. options= batters, pitchers.
        The default is None.
    fg : bool, optional
        If true, leverage the fangraphs prospects api endpoint to return the top 301 on FG.
        The default is False.
    year : int (YYYY), optional
        The year of the desired prospects report (FG only, current MLB endpoint does not support year subsetting).
        The default is date.today().year.

    Returns
    -------
    DataFrame
        Based on criteria in function params returns a df of topProspects.

    """
    if fg:
        url = f'https://www.fangraphs.com/api/prospects/board/prospects-list?statType=player&draft={year}prospect'
        topProspects = pd.DataFrame(json.loads(requests.get(url, timeout=None).text))
        if teamName != None:
            topProspects = topProspects.loc[topProspects.Team == teamName.upper()]
        if playerType == "batters":
            # TB: not in love with this method but using "Position" column could remove potential two-way players
            topBattingProspects = topProspects.loc[topProspects['Hit'] != '']
            return topBattingProspects
        elif playerType == "pitchers":
            topPitchingProspects = topProspects.loc[~topProspects['Vel'].isna()]
            return topPitchingProspects
        elif playerType == None:
            return topProspects
    else:
        url = "https://www.mlb.com/prospects/stats/top-prospects"
        res = requests.get(url, timeout=None).content
        prospectList = pd.read_html(res)
        if playerType == "batters":
            topBattingProspects = postprocess(prospectList[0])
            return topBattingProspects
        elif playerType == "pitchers":
            topPitchingProspects = postprocess(prospectList[1])
            return topPitchingProspects
        elif playerType == None:
            topProspects = pd.concat(prospectList)
            topProspects.sort_values(by=['Rk'], inplace = True)
            topProspects = postprocess(topProspects)
            return topProspects
