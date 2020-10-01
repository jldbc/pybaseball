import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from datahelpers import postprocessing
from typing import Dict, Optional, Tuple, Union
import bs4 as bs
import pandas as pd
import re


def download_url(url: str) -> bytes:
    """
    Gets the content from the url specified
    """
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    resp = session.get(url)
    return resp.content


def get_split_soup(playerid: str, year: Optional[int] = None, pitching_splits: bool = False) -> bs.BeautifulSoup:
    """
    gets soup for the player splits. 
    """
    pitch_or_bat = 'p' if pitching_splits else 'b'
    if year is None:  # provides scores from yesterday if date is not provided
        url = f"https://www.baseball-reference.com/players/split.fcgi?id={playerid}&year=Career&t={pitch_or_bat}"
    else:
        year = str(year)
        url = f"https://www.baseball-reference.com/players/split.fcgi?id={playerid}&year={year}&t={pitch_or_bat}"
    html = download_url(url)
    soup = bs.BeautifulSoup(html, 'lxml')
    return soup


def get_player_info(playerid: str, soup: bs.BeautifulSoup = None) -> Dict:
    '''
    Returns a dictionary with player position, batting and throwing handedness, player height in inches, player weight, and current team from Baseball Reference. 
    '''

    if not soup:
        soup = get_split_soup(playerid)
    about_info = soup.find_all(
        "div", {"itemtype": "https://schema.org/Person"})
    info = [ele for ele in about_info]
    # This for loop goes through the player bio section at the top of the splits page to find all of the <p> tags
    for i in range(len(info)):
        ptags = info[i].find_all('p')
        fv = []
        # This loop goes through each of the <p> tags and finds all text between the tags including the <strong> tags.
        for j in range(len(ptags)):
            InfoRegex = re.compile(r'>(.*?)<', re.DOTALL)
            r = InfoRegex.findall(str(ptags[j]))
            # This loop cleans up the text found in the outer loop and removes non alphanumeric characters.
            for k in range(len(r)):
                pattern = re.compile('[\W_]+')
                strings = pattern.sub(' ', r[k])
                if strings and strings != ' ':
                    fv.append(strings)
    player_info_data = {
        'Position': fv[1],
        'Bats': fv[3],
        'Throws': fv[5],
        'Height': int(fv[6].split(' ')[0])*12+int(fv[6].split(' ')[1]),
        'Weight': int(fv[7][0:3]),
        'Team': fv[10]
    }
    return player_info_data


def get_splits(playerid: str, year: Optional[int] = None, player_info: bool = False, pitching_splits: bool = False) -> Union[pd.DataFrame, Tuple[pd.DataFrame, Dict]]:
    """
    Returns a dataframe of all split stats for a given player.
    If player_info is True, this will also return a dictionary that includes player position, handedness, height, weight, position, and team
    """
    soup = get_split_soup(playerid, year, pitching_splits)
    # the splits tables on the bbref site are all within an embedded comment. This finds all the comments
    comment = soup.find_all(text=lambda text: isinstance(text, bs.Comment))
    data = []
    for i in range(len(comment)):
        commentsoup = bs.BeautifulSoup(comment[i], 'lxml')
        split_tables = commentsoup.find_all(
            "div", {"class": "overthrow table_container"})
        splits = [ele for ele in split_tables]
        headings = []
        for j in range(len(splits)):
            if year == None:  # The bbref tables for career splits have one extra preceding th column labeled 'I' that is not used and is not in the single season records
                headings = [th.get_text()
                            for th in splits[j].find("tr").find_all("th")][1:]
            else:
                headings = [th.get_text()
                            for th in splits[j].find("tr").find_all("th")][:]
            headings.append('Split Type')
            headings.append('Player ID')
            # singles data isn't included in the tables so this appends the column header
            headings.append('1B')
            data.append(headings)
            rows = splits[j].find_all('tr')
            for row in rows:
                if year == None:  # The bbref tables for career splits have one extra preceding th column labeled 'I' that is not used and is not in the single season records
                    cols = row.find_all('td')
                else:
                    cols = row.find_all(['th', 'td'])
                cols = [ele.text.strip() for ele in cols]
                split_type = splits[j].find_all('caption')[0].string.strip()
                if split_type != "By Inning":  # bbref added three empty columns to the by inning tables that don't match the rest of the tables. Not including this split table in results
                    cols.append(split_type)
                    cols.append(playerid)
                    data.append([ele for ele in cols])

    data = pd.DataFrame(data)
    data = data.rename(columns=data.iloc[0])
    data = data.reindex(data.index.drop(0))
    data = data.set_index(['Player ID', 'Split Type', 'Split'])
    data = data.drop(index=['Split'], level=2)
    data = data.apply(pd.to_numeric, errors='coerce')
    data = data.dropna(axis=1, how='all')
    data['1B'] = data['H']-data['2B']-data['3B']-data['HR']
    data = data.loc[playerid]
    if player_info == False:
        return data
    else:
        player_info_data = get_player_info(playerid=playerid, soup=soup)
        return data, player_info_data
