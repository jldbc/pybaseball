import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

# Team Abbreviations for easier querying
team_abbr = {'ARI' : 'arizona-diamondbacks', 'ATL': 'atlanta-braves', 'BAL': 'baltimore-orioles', 'BOS': 'boston-red-sox',
			 'CHC': 'chicago-cubs', 'CHW': 'chicago-white-sox', 'CIN': 'cincinnati-reds', 'CLE': 'cleveland-indians',
			 'COL': 'colorado-rockies', 'DET': 'detroit-tigers', 'HOU': 'houston-astros', 'KCR': 'kansas-city-royals',
			 'LAA': 'los-angeles-angels', 'LAD': 'los-angeles-dodgers', 'MIA': 'miami-marlins', 'MIL': 'milwaukee-brewers',
			 'MIN': 'minnesota-twins', 'NYM': 'new-york-mets', 'NYY': 'new-york-yankees', 'OAK': 'oakland-athletics',
			 'PHI': 'philadelphia-phillies', 'PIT': 'pittsburgh-pirates', 'SDP': 'san-diego-padres', 'SEA': 'seattle-mariners',
			 'SFG': 'san-francisco-giants', 'STL': 'st.-louis-cardinals', 'TBR': 'tampa-bay-rays', 'TEX': 'texas-rangers',
			 'TOR': 'toronto-blue-jays', 'WSN': 'washington-nationals'}

# Position abbreviations for easier querying
pos_abbr = {'AB': 'batters', 'C': 'catcher', 'IF': 'infield', '1B': '1st-base', '2B': '2nd-base', '3B': '3rd-base',
			'SS': 'shortstop', 'OF': 'outfield', 'RF': 'right-field', 'LF': 'left-field', 'CF': 'center-field',
			'DH': 'designated-hitter', 'P': 'pitching', 'SP': 'starting-pitcher', 'RP': 'relief-pitcher',
			'CP': 'closer'}

spotrac_salaries_url = "https://www.spotrac.com/mlb/rankings"

def get_soup(url):
	response = requests.get(url)
	soup = BeautifulSoup(response.content, 'html.parser')

	return soup

def format_cols(cols, season):
	"""
	Formats columns into format: [Year, PlayerName, Position, Salary]

	cols : list : List of data to be parsed
	season : Season being parsed
	"""

	player = cols[0].split('\n')[0]
	position = cols[0].split('\n')[1]
	salary = cols[1]

	return [season, player, position, salary]

def get_table(soup, season):
	data = []
	table = soup.find_all('table', {'class': 'datatable noborder'})[0]  # Gets table holding salary data

	rows = table.find_all('tr')
	for row in rows:
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols[2:]]  # sliced at 2 to remove rank and team image columns
		if len(cols) == 0:
			continue  # Ignore initial empty list
		# print(cols)
		cols = format_cols(cols, season)
		data.append([ele for ele in cols])

	return data

# PROBLEM: requests only return top 100 salaries. Not sure how to fix this yet.
def salaries_by_all(start_season, end_season=None, to_float=False):
	"""
	Get season-level player salaries for the entire league

	start_season : int : First season for which you want salary data.
	end_season : int : Last season for which you want salary data. If set to None, then will only get data for start_season.
	to_float : Set to True if you want to convert salary to float, otherwise leave as False.
	"""

	if start_season is None:
		raise ValueError("You need to provide at least one season to collect data for. Try salaries_by_team(season, team) or salaries_by_team(start_season, end_season, team).")
	if end_season is None:
		end_season = start_season

	data = []
	headings = ['Year', 'Player', 'Position', 'Salary']
	for season in range(start_season, end_season+1):
		season_salaries_url = "{}/{}".format(spotrac_salaries_url, season)
		soup = get_soup(season_salaries_url)

		table = get_table(soup, season)
		for col in table:
			data.append(col)

	data = pd.DataFrame(data=data, columns=headings)
	if to_float:
		data['Salary'] = data['Salary'].map(lambda x: x.lstrip('$').replace(',', '')).apply(float)

	return data

def salaries_by_team(team, start_season, end_season=None, to_float=False):
	"""
	Get season-level player salaries for a specified team and time-frame

	team : str : Abbreviation for the team you want to collect salary data (i.e. 'NYY' for New York Yankees).
	start_season : int : First season for which you want salary data.
	end_season : int : Last season for which you want salary data. If set to None, then will only get data for start_season.
	to_float : bool : Set to True if you want to convert salary to float, otherwise leave as False.
	"""

	if start_season is None:
		raise ValueError("You need to provide at least one season to collect data for. Try salaries_by_team(season, team) or salaries_by_team(start_season, end_season, team).")
	if team is None:
		raise ValueError("You must provide the team for which to collect salary data. If you want all salary data, try salaries_all(start_season, end_season).")
	if end_season is None:
		end_season = start_season

	data = []
	headings = ['Year', 'Player', 'Position', 'Salary']
	for season in range(start_season, end_season+1):
		season_salaries_url = "{}/{}/{}".format(spotrac_salaries_url, season, team_abbr[team])
		soup = get_soup(season_salaries_url)

		table = get_table(soup, season)
		for col in table:
			data.append(col)

	data = pd.DataFrame(data=data, columns=headings)
	if to_float:
		data['Salary'] = data['Salary'].map(lambda x: x.lstrip('$').replace(',', '')).apply(float)

	return data

def salaries_by_position(position, start_season, end_season=None, to_float=False):
	"""
	Get season-level player salaries for a specified position and timeframe

	position : str : Abbreviation for position you want to collect salary data (i.e. '1B' for first-base, or 'SP' for starting-pitcher).
	start_season : int : First season for which you want salary data.
	end_season : int : Last season for which you want salary data. If set to None, then will only get data for start_season.
	to_float : bool : Set to True if you want to convert salary to float, otherwise leave as False.
	"""
	if start_season is None:
		raise ValueError("You need to provide at least one season to collect data for. Try salaries_by_position(season, position) or salaries_by_position(start_season, end_season, team).")
	if position is None:
		raise ValueError("You must provide the position for which to collect salary data. If you want all salary data, try salaries_all(start_season, end_season).")
	if end_season is None:
		end_season = start_season

	data = []
	headings = ['Year', 'Player', 'Position', 'Salary']
	for season in range(start_season, end_season+1):
		season_salaries_url = "{}/{}/{}".format(spotrac_salaries_url, season, pos_abbr[position])
		soup = get_soup(season_salaries_url)

		table = get_table(soup, season)
		for col in table:
			data.append(col)

	data = pd.DataFrame(data=data, columns=headings)
	if to_float:
		data['Salary'] = data['Salary'].map(lambda x: x.lstrip('$').replace(',', '')).apply(float)

	return data



if __name__ == '__main__':
	print(salaries_by_all(2018))
	# print(salaries_by_team(2018, team='MIL', to_float=True))
	# print(salaries_by_position(2018, 2018, position='SP', to_float=False))



