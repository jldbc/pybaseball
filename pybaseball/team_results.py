import pandas as pd
import requests
from bs4 import BeautifulSoup

# TODO: raise error if year > current year or < first year of a team's existence
# TODO: team validation. return error if team does not exist. 
# TODO: sanitize team inputs (force to all caps)
# TODO: translate streak to a number (+++ / --- format is not very useful)
# TODO: convert some cols to numeric. this include dropping commas in attendance numbers.
# TODO: all teams? a full season's worth of results

def get_soup(season, team):
	# get most recent year's schedule if year not specified
	if(season is None):
		season = datetime.datetime.today().strftime("%Y")
	url = "http://www.baseball-reference.com/teams/{}/{}-schedule-scores.shtml".format(team, season)
	s=requests.get(url).content
	return BeautifulSoup(s, "html.parser")

def get_table(soup):
	table = soup.find_all('table')[0]
	data = []
	headings = [th.get_text() for th in table.find("tr").find_all("th")]
	headings = headings[1:] # the "gm#" heading doesn't have a <td> element
	headings[3] = "Home_Away"
	data.append(headings)
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')
	for row_index in range(len(rows)-1): #last row is a description of column meanings
		row = rows[row_index]
		try:
			cols = row.find_all('td')
			#links = row.find_all('a')
			if cols[3].text == "":
				cols[3].string = 'Home' # this element only has an entry if it's an away game
			if cols[12].text == "":
				cols[12].string = "None" # tie games won't have a pitcher win or loss
			if cols[13].text == "":
				cols[13].string = "None"
			if cols[14].text == "":
				cols[14].string = "None" # games w/o saves have blank td entry
			if cols[8].text == "":
				cols[8].string = "9" # entry is blank if no extra innings
			cols = [ele.text.strip() for ele in cols]
			data.append([ele for ele in cols if ele])
		except:
			# two cases will break the above: games that haven't happened yet, and BR's redundant mid-table headers
			# if future games, grab the scheduling info. Otherwise do nothing. 
			if len(cols)>1:
				cols = [ele.text.strip() for ele in cols][0:5]
				data.append([ele for ele in cols if ele])
	#convert to pandas dataframe. make first row the table's column names and reindex. 
	data = pd.DataFrame(data)
	data = data.rename(columns=data.iloc[0])
	data = data.reindex(data.index.drop(0))
	return data

def schedule_and_record(season=None, team=None):
	# retrieve html from baseball reference
	soup = get_soup(season, team)
	table = get_table(soup)
	return table
