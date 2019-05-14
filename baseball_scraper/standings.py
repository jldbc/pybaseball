from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import datetime
import pandas as pd 

def get_soup(year):
    url = 'http://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(year)
    s=requests.get(url).content
    return BeautifulSoup(s, "lxml")

def get_tables(soup, season):
    datasets = []
    if(season>=1969):
        tables = soup.find_all('table')
        for table in tables:
            data = []
            headings = [th.get_text() for th in table.find("tr").find_all("th")]
            data.append(headings)
            table_body = table.find('tbody')
            rows = table_body.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                cols = [ele.text.strip() for ele in cols]
                cols.insert(0,row.find_all('a')[0]['title']) # team name
                data.append([ele for ele in cols if ele])
            datasets.append(data)
    else:
        data = []
        table = soup.find('table')
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        headings[0] = "Name"
        if(season>=1930):
            for i in range(15): headings.pop()
        elif(season>=1876): 
            for i in range(14): headings.pop()
        else:
            for i in range(16): headings.pop()
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            if row.find_all('a') == []: continue
            cols = row.find_all('td')
            if(season>=1930):
                for i in range(15): cols.pop()
            elif(season>=1876): 
                for i in range(14): cols.pop()
            else:
                for i in range(16): cols.pop()
            cols = [ele.text.strip() for ele in cols]
            cols.insert(0,row.find_all('a')[0]['title']) # team name
            data.append([ele for ele in cols if ele])
        datasets.append(data)
    #convert list-of-lists to dataframes
    for idx in range(len(datasets)):
        datasets[idx] = pd.DataFrame(datasets[idx])
    return datasets #returns a list of dataframes

def standings(season=None):
    # get most recent standings if date not specified
    if(season is None):
        season = int(datetime.datetime.today().strftime("%Y"))
    if season<1871:
        raise ValueError("This query currently only returns standings until the 1871 season. Try looking at years from 1871 to present.")
    # retrieve html from baseball reference
    soup = get_soup(season)
    if season>=1969:
        tables = get_tables(soup, season)
    else:
        t = soup.find_all(string=lambda text:isinstance(text,Comment))
        # list of seasons whose table placement breaks the site's usual pattern
        exceptions = [1884, 1885, 1886, 1887, 1888, 1889, 1890, 1892, 1903]
        if (season>1904 or season in exceptions): code = BeautifulSoup(t[16], "lxml")
        elif season<=1904: code = BeautifulSoup(t[15], "lxml")
        tables = get_tables(code, season)
    tables = [pd.DataFrame(table) for table in tables]
    for idx in range(len(tables)):
        tables[idx] = tables[idx].rename(columns=tables[idx].iloc[0])
        tables[idx] = tables[idx].reindex(tables[idx].index.drop(0))
    return tables
