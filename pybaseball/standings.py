from bs4 import BeautifulSoup
from bs4 import Comment
import requests
import datetime
import pandas as pd 

def get_soup(year):
    url = 'http://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(year)
    s=requests.get(url).content
    return BeautifulSoup(s, "html.parser")

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
        tables = soup.find('table')
        headings = [th.get_text() for th in table.find("tr").find_all("th")]
        headings[0] = "Name"
        if(season>=1930):
            for i in range(15): headings.pop()
        else:
            for i in range(14): headings.pop()
        data.append(headings)
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            if row.find_all('a') == []: continue
            cols = row.find_all('td')
            if(season>=1930):
                for i in range(15): cols.pop()
            else:
                for i in range(14): cols.pop()
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
    if season<1903:
        raise ValueError("This query currently only returns standings until the 1903 season. Try looking at years from 1903 to present.")
    # retrieve html from baseball reference
    soup = get_soup(season)
    if season>=1969:
        tables = get_tables(soup, season)
    elif season>=1903:
        t = soup.find_all(string=lambda text:isinstance(text,Comment))
        code = None
        for i, c in enumerate(t):
            if i==17: code = BeautifulSoup(c, "html.parser")
        tables = get_tables(code, season)
    tables = [pd.DataFrame(table) for table in tables]
    for idx in range(len(tables)):
        tables[idx] = tables[idx].rename(columns=tables[idx].iloc[0])
        tables[idx] = tables[idx].reindex(tables[idx].index.drop(0))
    return tables
