import requests
import pandas as pd
from bs4 import BeautifulSoup

def get_soup(start_dt, end_dt):
	# get most recent standings if date not specified
	if((start_dt is None) or (end_dt is None)):
		print('Error: a date range needs to be specified')
		return None
	url = "http://www.baseball-reference.com/leagues/daily.cgi?user_team=&bust_cache=&type=b&lastndays=7&dates=fromandto&fromandto={}.{}&level=mlb&franch=&stat=&stat_value=0".format(start_dt, end_dt)
	s=requests.get(url).content
	return BeautifulSoup(s, "html.parser")

def get_table(soup):
	table = soup.find_all('table')[0]
	data = []
	headings = [th.get_text() for th in table.find("tr").find_all("th")][1:]
	data.append(headings)
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')
	for row in rows:
	    cols = row.find_all('td')
	    cols = [ele.text.strip() for ele in cols]
	    data.append([ele for ele in cols])# if ele])
	data = pd.DataFrame(data)
	data = data.rename(columns=data.iloc[0])
	data = data.reindex(data.index.drop(0))
	return data

def batting_stats_range(start_dt=None, end_dt=None):
	"""
	Get all batting stats for a set time range. This can be the past week, the month of 
	August, anything. Just supply the start and end date in YYYY-MM-DD format. 
	"""
	# retrieve html from baseball reference
	soup = get_soup(start_dt, end_dt)
	table = get_table(soup)
	table = table.dropna(how='all') # drop if all columns are NA
	# scraped data is initially in string format. convert the necessary columns to numeric.
	for column in ['Age', '#days', 'G', 'PA', 'AB', 'R', 'H', '2B', '3B',
					'HR', 'RBI', 'BB', 'IBB', 'SO', 'HBP', 'SH', 'SF', 'GDP',
					'SB', 'CS', 'BA', 'OBP', 'SLG', 'OPS']:
		#table[column] = table[column].astype('float')
		table[column] = pd.to_numeric(table[column])

	return table

def batting_stats(season=None):
	"""
	Get all batting stats for a set season. If no argument is supplied, gives stats for 
	current season to date. 
	"""
	if season == None:
		season = datetime.datetime.today().strftime("%Y")
	season = str(season)
	start_dt = season + '-03-01' #opening day is always late march or early april
	end_dt = season + '-11-01' #season is definitely over by November 
	return(batting_stats_range(start_dt, end_dt))

