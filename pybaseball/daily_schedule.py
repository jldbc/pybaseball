import calendar
import re
from datetime import date, datetime

import pandas as pd
from bs4 import BeautifulSoup, Tag

from . import cache
from .datasources.bref import BRefSession

MAIN_SCHEDULE_HEADER = 'MLB Schedule'
POSTSEASON_HEADER = 'Postseason Schedule'

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

        game['road_team_score'] = None
        game['home_team_score'] = None
    else:
        game['start_time'] = None

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

def _get_games_from_date_h3(date_h3: Tag, postseason_h2: Tag) -> [dict]:
    games = []

    today = date.today();
    today_str = (f'{calendar.day_name[today.weekday()]}, {calendar.month_name[today.month]}'
                        f' {today.day}, {today.year}')

    for sibling in date_h3.find_next_siblings('p', attrs={'class': 'game'}):
        game_dict = _convert_tag_to_dict(sibling, postseason_h2)
        game_dict['date'] = date_h3.text if date_h3.text != 'Today\'s Games' else today_str

        games.append(game_dict)

    return games

# h2 indicating start of postseason games on page. will be used to determine if a given game
# is postseason or not
def _get_postseason_h2(soup: BeautifulSoup) -> Tag:
    return soup.find(lambda tag: tag.name == 'h2' and POSTSEASON_HEADER in tag.text)

def get_soup() -> BeautifulSoup:
    # bref only has public pages for the current or immediately previous season
    url = 'https://www.baseball-reference.com/leagues/MLB-schedule.shtml'
    s = session.get(url).content
    return BeautifulSoup(s, "lxml")

@cache.df_cache(expires=1)
def daily_schedule(dates: [datetime] = date.today()) -> pd.DataFrame:
    soup = get_soup()

    today = date.today()

    # make parameter iterable if it's not
    if not isinstance(dates, list):
        dates = [dates]

    # used to determine if a game is postseason or not
    postseason_h2 = _get_postseason_h2(soup)

    # a list of dictionaries that we'll turn into a df
    games = []

    for day in dates:
        # today has a special label on the page
        if day == today:
            date_str = 'Today\'s Games'
        else:
            # format we want for date
            date_str = (f'{calendar.day_name[day.weekday()]}, {calendar.month_name[day.month]}'
                        f' {day.day}, {day.year}')

        # find the h3 with the right text
        date_h3 = soup.find(lambda tag: tag.name == 'h3' and date_str in tag.text)

        # return skip further processing for this date if there are no games scheduled
        if not date_h3:
            continue

        games.extend(_get_games_from_date_h3(date_h3, postseason_h2))

    # convert to a dataframe
    return pd.DataFrame(games)

@cache.df_cache()
def full_schedule() -> pd.DataFrame:
    soup = get_soup()

    # a list of dictionaries that we'll turn into a df
    games = []

    # get MLB Schedule h2 tag
    schedule_h2 = soup.find(lambda tag: tag.name == 'h2' and MAIN_SCHEDULE_HEADER in tag.text)

    # short circuit if markup is not formatted as expected
    if not schedule_h2:
        return pd.DataFrame()

    schedule_container = schedule_h2.parent.parent

    # used to determine if a game is postseason or not
    postseason_h2 = _get_postseason_h2(soup)

    for h3_tag in schedule_container.find_all('h3'):
        games.extend(_get_games_from_date_h3(h3_tag, postseason_h2))

    # convert to a dataframe
    return pd.DataFrame(games)