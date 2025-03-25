import calendar
import re
from datetime import date

import pandas as pd
from bs4 import BeautifulSoup, Tag

from . import cache
from .datasources.bref import BRefSession

REGULAR_SEASON = 'reg'
POSTSEASON = 'post'
SPRING_TRAINING = 'spring'
SCORE_PATTERN = r'\((\d*)\)'

session = BRefSession()

# convert a <p> tag on the page containing info about a game to a dict with the fields we want
def _convert_tag_to_dict(game_tag: Tag, postseason_h2) -> dict:
    game = {}

    if not game_tag:
        return game

    team_anchors = game_tag.find_all('a')
    game['road_team'] = team_anchors[0].text
    game['home_team'] = team_anchors[1].text

    # find time <span>
    time_span = game_tag.find('span', attrs={'tz': True})

    # if there's a time_span the game is either in the future or a spring training game. in either case
    # there is no score associated. if there isn't a time_span, there will be score info
    if time_span:
        time_strong = time_span.find('strong')
        game['start_time'] = time_strong.text if time_strong else None
    else:
        # capture the numbers in parantheses, they're the score
        match = re.findall(SCORE_PATTERN, game_tag.text)

        game['road_team_score'] = match[0]
        game['home_team_score'] = match[1]

    # check to see if date_h3 is in the same tree as postseason_h2. if it is, it's a postseason game
    if postseason_h2 and postseason_h2.parent.parent == game_tag.parent.parent.parent:
        game['type'] = POSTSEASON
    elif game_tag.find(lambda tag: tag.name == 'span' and tag.text == '(Spring)'):
        game['type'] = SPRING_TRAINING
    else:
        game['type'] = REGULAR_SEASON

    return game

def get_soup() -> BeautifulSoup:
    # bref only has public pages for the current or immediately previous season
    url = 'https://www.baseball-reference.com/leagues/MLB-schedule.shtml'
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

@cache.df_cache()
def daily_schedule(day=date.today()) -> pd.DataFrame:
    soup = get_soup()

    today = date.today()

    # today has a special label on the page
    if day == today:
        date_str = 'Today\'s Games'
    else:
        # format we want for date
        date_str = (f'{calendar.day_name[day.weekday()]}, {calendar.month_name[day.month]}'
                    f' {day.day}, {day.year}')

    # find the h3 with the right text
    date_h3 = soup.find(lambda tag: tag.name == 'h3' and date_str in tag.text)

    # return empty frame if no games scheduled for the day
    if not date_h3:
        return pd.DataFrame()

    # a list of dictionaries that we'll turn into a df
    games = []

    # h2 indicating start of postseason games on page
    postseason_h2 = soup.find(lambda tag: tag.name == 'h2' and 'Postseason Schedule' in tag.text)

    for sibling in date_h3.find_next_siblings('p', attrs={'class': 'game'}):
        games.append(_convert_tag_to_dict(sibling, postseason_h2))

    # convert to a dataframe
    return pd.DataFrame(games)
