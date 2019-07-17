import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests

def get_soup(start_season, end_season, league, qual, ind):
    url = "http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual={}&type=c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,287,288,289,290,291,292,293,294,295,296,297,298,299,-1&season={}&month=0&season1={}&ind={}&team=&rost=&age=&filter=&players=&page=1_100000"
    url = url.format(league, qual, end_season, start_season, ind)
    s=requests.get(url).content
    #print(s)
    return BeautifulSoup(s, "lxml")

def get_table(soup, ind):
    table = soup.find('table', {'class': 'rgMasterTable'})

    data = []
    # pulls headings from the fangraphs table
    headings = []
    headingrows = table.find_all('th')
    for row in headingrows[1:]:
        headings.append(row.text.strip())
    
    data.append(headings)
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        cols = [ele.text.strip() for ele in cols]
        data.append([ele for ele in cols[1:]])

    data = pd.DataFrame(data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))

    # replace emptry strings with NaN
    data.replace(r'^\s*$', np.nan, regex=True, inplace = True)

    # convert all percent strings to proper percetages
    percentages = ['Contact% (pi)', 'Zone% (pi)','Z-Contact% (pi)','O-Contact% (pi)','Swing% (pi)','Z-Swing% (pi)','O-Swing% (pi)','SL% (pi)','SI% (pi)','SB% (pi)','KN% (pi)','FS% (pi)','FC% (pi)','FA% (pi)','CU% (pi)','CS% (pi)','CH% (pi)','TTO%','Hard%','Med%','Soft%','Oppo%','Cent%','Pull%','K-BB%','Zone% (pfx)','Contact% (pfx)','Z-Contact% (pfx)','O-Contact% (pfx)','Swing% (pfx)','Z-Swing% (pfx)','O-Swing% (pfx)','UN% (pfx)','KN% (pfx)','SC% (pfx)','CH% (pfx)','EP% (pfx)','KC% (pfx)','CU% (pfx)','SL% (pfx)','SI% (pfx)','FO% (pfx)','FS% (pfx)','FC% (pfx)','FT% (pfx)','FA% (pfx)','BB%','K%','SwStr%','F-Strike%','Zone%','Contact%','Z-Contact%','O-Contact%','Swing%','Z-Swing%','O-Swing%','XX%','KN%','SF%','CH%','CB%','CT%','SL%','FB%','BUH%','IFH%','HR/FB','IFFB%','GB%','LD%','LOB%', 'XX% (pi)', 'PO%']
    for col in percentages:
        # skip if column is all NA (happens for some of the more obscure stats + in older seasons)
        if not data[col].empty:
            if pd.api.types.is_string_dtype(data[col]):
                data[col] = data[col].astype(str).str.strip(' %')
                data[col] = data[col].astype(str).str.strip('%')
                data[col] = data[col].astype(float)/100.
        else:
            #print(col)
            pass

    #convert everything except name and team to numeric
    cols_to_numeric = [col for col in data.columns if col not in ['Name', 'Team', 'Age Rng', 'Dollars']]
    data[cols_to_numeric] = data[cols_to_numeric].astype(float)

    #sort by WAR and wins so best players float to the top
    data = data.sort_values(['WAR', 'W'], ascending=False)
    #put WAR at the end because it looks better
    cols = data.columns.tolist()
    cols.insert(7, cols.pop(cols.index('WAR')))
    data = data.reindex(columns= cols)
    return data

def pitching_stats(start_season, end_season=None, league='all', qual=1, ind=1):
    """
    Get season-level pitching data from FanGraphs. 

    ARGUMENTS:
    start_season : int : first season you want data for (or the only season if you do not specify an end_season)
    end_season : int : final season you want data for 
    league : "all", "nl", or "al"
    qual: minimum number of pitches thrown to be included in the data (integer). Use the string 'y' for fangraphs default.
    ind : int : =1 if you want individual season-level data, =0 if you want a player's aggreagate data over all seasons in the query
    """
    if start_season is None:
        raise ValueError("You need to provide at least one season to collect data for. Try pitching_leaders(season) or pitching_leaders(start_season, end_season).")
    if end_season is None:
        end_season = start_season
    soup = get_soup(start_season=start_season, end_season=end_season, league=league, qual=qual, ind=ind)
    table = get_table(soup, ind)
    return table
