from bs4 import BeautifulSoup
import pandas as pd
import requests

def get_table(soup):
	data = []

	table = soup.find_all('table', {'id': 'batting_standard'})[0]
	headings = [row.text.strip() for row in table.find_all('th')[0:30]]

	rows = table.find_all('tr')[:-9][1:] # :-9 to remove totals and other unwanted rows | 1: to remove headings
	for row in rows:
		year = row.find('th').text
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols]
		cols.insert(0, year) # insert year at beginning of columns
		# cols = [col.replace('*', '').replace('#', '') for col in cols]  # Removes '*' and '#' from some names
		data.append([ele for ele in cols[0:]])

	data = pd.DataFrame(data=data, columns=headings)# [:-5]  # -5 to remove Team Totals and other rows
	data = data.dropna()  # Removes Row of All Nones

	return data

def player_batting_bref(bref_id):
	"""
	Gets career batting stats for a single player (from baseball-reference).

	bref_id : str : Identifier used on Baseball-Reference (can be acquired using 'pybaseball.playerid_lookup')

	return : DataFrame : Pandas DataFrame containing available career batting stats for the specified player.
	"""
	url = "https://www.baseball-reference.com/players/r/{}.shtml".format(bref_id)
	response = requests.get(url)
	soup = BeautifulSoup(response.content, 'html.parser')

	data = get_table(soup)

	return data


if __name__ == '__main__':
	ruth = player_batting_bref('ruthba01')

	print(ruth)