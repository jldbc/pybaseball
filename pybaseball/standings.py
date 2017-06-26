from bs4 import BeautifulSoup
import requests
import datetime

def get_soup(date):
	#year, month, day = [today.strftime("%Y"), today.strftime("%m"), today.strftime("%d")]
	#url = "http://www.baseball-reference.com/boxes?year={}&month={}&day={}".format(year, month, day)
	year = date.strftime("%Y")
	url = 'http://www.baseball-reference.com/leagues/MLB/{}-standings.shtml'.format(year)
	s=requests.get(url).content
	return BeautifulSoup(s)

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
			#data.append(row.find_all('a')[0]['title'])  # team name
		    cols = row.find_all('td')
		    cols = [ele.text.strip() for ele in cols]
		    cols.insert(0,row.find_all('a')[0]['title'])
		    data.append([ele for ele in cols if ele])
		datasets.append(data)
	return datasets


def standings(date=None):
	# get most recent standings if date not specified
	if(date is None):
		date = datetime.datetime.today()
	# retrieve html from baseball reference
	soup = get_soup(date)
	tables = get_tables(soup)
	return tables

