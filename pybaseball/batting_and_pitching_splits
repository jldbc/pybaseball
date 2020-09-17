import requests
import pandas as pd
import bs4 as bs
import concurrent.futures   
import re

def download_url(url):
    """
    Creates a single dictionary entry with the contents of each table requested as {'playerid':content}
    """
    urlcontent={}
    resp=requests.get(url)
    urlRegex=re.compile(r'%3Fid%3D(.*)%26year%3D(.*)%26t%3D(.*)&div=div_(.*)')
    title=urlRegex.search(url).group(1)+'-'+urlRegex.search(url).group(4)
    urlcontent[title]=resp.content
    return urlcontent
    
def download_tables(table_urls):
    """
    reads each split table provided from bbref concurrently and outputs a dictionary of the titles generated in download_url and the response content
    """
    threads=min(30, len(table_urls))
    data={}    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,threads)) as executor:
        futurecontent={executor.submit(download_url, url): url for url in table_urls}
        for future in concurrent.futures.as_completed(futurecontent):
            data.update(future.result())        
    return data


def read_split_files(urls,content):
    """
    reads the split dictionary that was created and outputs a multi-index dataframe of stats indexed by playerid, split type, and split. 
    """
    
    data=[]
    for i in content:
        html=content[i]
        soup=bs.BeautifulSoup(html, 'lxml')
        playerid=i.split('-')[0]
        split=i.split('-')[1]
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
    data = data.drop(index=['Split'], level=2)
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.fillna(0.0)
    data['1B']=data['H']-data['2B']-data['3B']-data['HR'] #populates the 1B column based on the other columns
    return data        

def find_split_urls(playerids, splits, pitching_split=False, season=None):
    """
    Get the urls from baseball reference for split data for each player id. Returns the set of URLs 
    for the playerid and splits provided. 
    default for pitching_split is False and will return the batting splits. 
    When pitching_split=True, pitching splits will be returned
    To get all batting split data tables, pass in 
    splits=['power', 'plato', 'gbfb', 'clutc', 'lever', 'count', 
            'hmvis', 'month', 'outcb', 'stsub', 'half', 'leado', 
            'lineu', 'outs', 'bases', 'times', 'hitlo', 'traj', 
            'oppon', 'stad', 'total', 'site']

    To get all pitching splits, pass in
    splits=['total',  'plato', 'hmvis', 'half', 'month', 'outco', 
            'sprel', 'rs', 'lineu', 'tkswg', 'count', 'leado', 
            'defpo', 'outs', 'bases', 'clutc', 'lever', 'innng', 
            'times', 'pitco', 'dr', 'hitlo', 'traj', 'oppon', 
            'stad', 'site', 'catch', 'ump'] 
    """
    if season is None:
        season='career'
    season=str(season)
    if pitching_split==True:
        pitch_or_bat='p'
    else:
        pitch_or_bat='b'
    links=[]
    content={}
    for playerid in playerids:
        for split in splits:
            url=f"https://widgets.sports-reference.com/wg.fcgi?css=1&site=br&url=%2Fplayers%2Fsplit.fcgi%3Fid%3D{playerid}%26year%3D{season}%26t%3D{pitch_or_bat}&div=div_{split}"
            links.append(url)
            content.update(download_tables(links))
    data=read_split_files(links,content) #reads and combines tables into a single dataframe
    return data