import pandas as pd
import requests

from . import cache

from pybaseball import teamid_lookup


@cache.df_cache()
def top_prospects(teamName=None, playerType=None):
    
    if teamName == None:
        url = "https://www.mlb.com/prospects/stats/top-prospects"
    else:
        mlbTeamId = teamid_lookup.mlb_team_id(teamName)
        url = f"https://www.mlb.com/prospects/stats?teamId={mlbTeamId}"
    
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


def postprocess(prospectList):        
    prospectList = prospectList.drop(list(prospectList.filter(regex = 'Tm|Unnamed:*')), axis = 1)    
    return prospectList