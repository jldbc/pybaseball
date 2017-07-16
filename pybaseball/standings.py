from bs4 import BeautifulSoup
import requests
import datetime
import pandas as pd 

def get_soup(year):
	# get most recent standings if date not specified
	if(year is None):
		year = datetime.datetime.today().strftime("%Y")
	url = 'http://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(year)
	s=requests.get(url).content
	return BeautifulSoup(s, "html.parser")

def get_tables(soup):
	tables = soup.find_all('table')
	datasets = []
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
	#convert list-of-lists to dataframes
	for idx in range(len(datasets)):
		datasets[idx] = pd.DataFrame(datasets[idx])
	return datasets #returns a list of dataframes

def standings(season=None):
	if season<1969:
		raise ValueError("This query currently only returns division standings, which did not exist until the 1969 season. Try looking at years from 1969 to present.")
	# retrieve html from baseball reference
	soup = get_soup(season)
	tables = get_tables(soup)
	tables = [pd.DataFrame(table) for table in tables]
	for idx in range(len(tables)):
		tables[idx] = tables[idx].rename(columns=tables[idx].iloc[0])
		tables[idx] = tables[idx].reindex(tables[idx].index.drop(0))
	return tables
