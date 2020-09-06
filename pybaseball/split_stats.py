import requests
import pandas as pd
import datetime
import io
from bs4 import BeautifulSoup
import bs4 as bs
import concurrent.futures   

def download_url(url):
    """
    Creates a local file with the contents of each table
    """
    resp=requests.get(url)
    title="".join(x for x in url if x.isalpha())+"html"
    
    with open(title, "wb") as fh:
        fh.write(resp.content)
    
def download_tables(table_urls):
    threads=min(30, len(table_urls))
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,threads)) as executor:
        executor.map(download_url, table_urls)
        

def read_split_files(urls):
    """
    reads the split files that were created and outputs a dataframe of stats by split. 
    """
    html=[]
    data=[]
    for i in range(len(urls)):
        with open("".join(x for x in urls[i] if x.isalpha())+"html") as f:
            html=f.read()
        soup=bs.BeautifulSoup(html, 'lxml')
        playerid=urls[i].split('%3D')[1].split('%26year')[0]
        split=urls[i].split('div_')[-1]
        table = soup.find_all('table')[0]
        headings = [th.get_text() for th in table.find("tr").find_all("th")][1:]
        headings.append('Split Type')
        headings.append('Player ID')
        headings.append('1B') #singles data isn't included in the tables so this appends the column header
        data.append(headings)
        table=soup.find('div')
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            cols.append(split)
            cols.append(playerid)
            data.append([ele for ele in cols])
    data = pd.DataFrame(data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))
    data = data.set_index(['Player ID', 'Split Type', 'Split'])
    data = data.drop(index=['Split'], 
                            level=2)
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.fillna(0.0)
    data = data.iloc[:,:-3]
    data['1B']=data['H']-data['2B']-data['3B']-data['HR'] #populates the 1B column based on the other columns
    return data

def file_check(urls):
    """
    Determines if data requested has already been downloaded
    """
    urls_to_get=[]
    for i in range(len(urls)):
        try:
            with open("".join(x for x in urls[i] if x.isalpha())+"html") as f:
                html=f.read()            
        except FileNotFoundError:
            urls_to_get.append(urls[i])
        else:
            try:
                soup=bs.BeautifulSoup(html, 'lxml')
                soup.find_all('table')[0]
            except IndexError:
                urls_to_get.append(urls[i])
    return(urls_to_get)

def find_split_urls(playerids, splits, PitchOrBat='b', season=None):
    """
    Get the urls from baseball reference for split data for each player id. Returns the set of URLs 
    for the playerid and splits provided. 
    Use PitchOrBat='b' for batting splits or , PitchOrBat='p' for pitching splits
    To get all batting split data tables, pass in 
    splits=['power', 'plato', 'gbfb', 'clutc', 'lever', 'count', 'hmvis', 'month', 'outcb', 'stsub', 'half', 'leado', 'lineu', 'outs', 'bases', 'times', 'hitlo', 'traj', 'oppon', 'stad', 'total', 'site']
        total - Season/Career Totals, last 7 days, last 14 days, last 28 days, last 365 days
        power - vs Power/Finesse Pitchers splits
        plato - platoon splits (e.g. vs RHP, vs LHP)
        gbfb - vs Ground Ball/Fly Ball Pitchers
        clutc - clutch stats (e.g. 2 outs RISP, Late & Close, Tie Game)
        lever - Leverage splits
        count - Count/Ball-Strikes
        hmvis - home or away splits
        month - month splits
        outcb - game outcome for team splits (in wins, in losses)
        stsub - starter or substitue splits
        half - first or second half splits
        leado - leading off the inning splits 
        lineu - batting order position splits
        outs - number of outs in inning  
        bases - bases occupied 
        times - times facing opponent in game
        hitlo - hit location splits
        traj - Hit trajectory (e.g. Ground balls, flyballs, line drives, bunts)
        oppon - opponent splits
        stad - game conditions
        site - ballpark


    To get all pitching splits, pass in
    ['total',  'plato', 'hmvis', 'half', 'month', 'outco', 'sprel', 'rs', 'lineu', 'tkswg', 'count', 'leado', 'defpo', 'outs', 'bases', 'clutc', 'lever', 'innng', 'times', 'pitco', 'dr', 'hitlo', 'traj', 'oppon', 'stad', 'site', 'catch', 'ump'] 
        total - Season/Career Totals, last 7 days, last 14 days, last 28 days, last 365 days
        plato - platoon splits (e.g. vs RHP, vs LHP)
        hmvis - home or away splits
        half - first or second half splits
        month - month splits
        outco - game outcome for team splits (in wins, in losses)
        sprel - Pitching Role (as starter, as reliever)
        rs - Run Support splits
        lineu - Batting order positions
        tkswg - Swung or took first pitch of PA
        count - Count/Balls-Strikes
        leado - Leading off Inning
        defpo - Defensive position (vs pitcher, vs non-pitcher)
        outs - Number of outs in inning
        bases - Bases occupied
        clutc - Clutch Stats
        lever - Leverage
        innng - By inning
        times - Times facing opponent in Game
        pitco - Pitch count
        dr - Days of Rest
        hitlo - Hit Location
        traj - Hit Trajectory
        oppon - opponent splits
        stad - game conditions  
        site - ballpark
        catch - By Catcher
        ump - By Umpire

    """
    if season is None:
        season='career'
    season=str(season)
    links=[]
    for playerid in playerids:
        for split in splits:
            url=["https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2Fsplit.fcgi%3Fid%3D"+playerid+"%26year%3D"+season+"%26t%3D"+PitchOrBat+"&div=div_"+split]            
            links+=url
    urls=file_check(links) #checks if data already exists
    download_tables(urls) #gets remaining tables
    data=read_split_files(links) #reads and combines tables into a single dataframe
    return data

