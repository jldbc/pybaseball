import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_soup(start_season, end_season, league, qual, ind):
	url = "http://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg={}&qual={}&type=c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211&season={}&month=0&season1={}&ind={}&team=&rost=&age=&filter=&players=&page=1_100000".format(league, qual, start_season, end_season, ind)
	s=requests.get(url).content
	return BeautifulSoup(s, "html.parser")

def get_table(soup):
	#doesn't work yet
	tables = soup.find_all('table')
	table = tables[10]
	data = []
	# couldn't find these in the table, hardcoding for now
	headings = ["Name","Team","Age","G","AB","PA","H","1B","2B","3B","HR","R","RBI","BB","IBB","SO","HBP","SF","SH","GDP","SB","CS","AVG","GB","FB","LD","IFFB","Pitches","Balls","Strikes","IFH","BU","BUH","BB%","K%","BB/K","OBP","SLG","OPS","ISO","BABIP","GB/FB","LD%","GB%","FB%","IFFB%","HR/FB","IFH%","BUH%","wOBA","wRAA","wRC","Bat","Fld","Rep","Pos","RAR","WAR","Dol","Spd","wRC+","WPA","-WPA","+WPA","RE24","REW","pLI","phLI","PH","WPA/LI","Clutch","FB%","FBv","SL%","SLv","CT%","CTv","CB%","CBv","CH%","CHv","SF%","SFv","KN%","KNv","XX%","PO%","wFB","wSL","wCT","wCB","wCH","wSF","wKN","wFB/C","wSL/C","wCT/C","wCB/C","wCH/C","wSF/C","wKN/C","O-Swing%","Z-Swing%","Swing%","O-Contact%","Z-Contact%","Contact%","Zone%","F-Strike%","SwStr%","BsR","FA% (pfx)","FT% (pfx)","FC% (pfx)","FS% (pfx)","FO% (pfx)","SI% (pfx)","SL% (pfx)","CU% (pfx)","KC% (pfx)","EP% (pfx)","CH% (pfx)","SC% (pfx)","KN% (pfx)","UN% (pfx)","vFA (pfx)","vFT (pfx)","vFC (pfx)","vFS (pfx)","vFO (pfx)","vSI (pfx)","vSL (pfx)","vCU (pfx)","vKC (pfx)","vEP (pfx)","vCH (pfx)","vSC (pfx)","vKN (pfx)","FA-X (pfx)","FT-X (pfx)","FC-X (pfx)","FS-X (pfx)","FO-X (pfx)","SI-X (pfx)","SL-X (pfx)","CU-X (pfx)","KC-X (pfx)","EP-X (pfx)","CH-X (pfx)","SC-X (pfx)","KN-X (pfx)","FA-Z (pfx)","FT-Z (pfx)","FC-Z (pfx)","FS-Z (pfx)","FO-Z (pfx)","SI-Z (pfx)","SL-Z (pfx)","CU-Z (pfx)","KC-Z (pfx)","EP-Z (pfx)","CH-Z (pfx)","SC-Z (pfx)","KN-Z (pfx)","wFA (pfx)","wFT (pfx)","wFC (pfx)","wFS (pfx)","wFO (pfx)","wSI (pfx)","wSL (pfx)","wCU (pfx)","wKC (pfx)","wEP (pfx)","wCH (pfx)","wSC (pfx)","wKN (pfx)","wFA/C (pfx)","wFT/C (pfx)","wFC/C (pfx)","wFS/C (pfx)","wFO/C (pfx)","wSI/C (pfx)","wSL/C (pfx)","wCU/C (pfx)","wKC/C (pfx)","wEP/C (pfx)","wCH/C (pfx)","wSC/C (pfx)","wKN/C (pfx)","O-Swing% (pfx)","Z-Swing% (pfx)","Swing% (pfx)","O-Contact% (pfx)","Z-Contact% (pfx)","Contact% (pfx)","Zone% (pfx)","Pace","Def","wSB","UBR","Age Rng","Off","Lg","wGDP","Pull%","Cent%","Oppo%","Soft%","Med%","Hard%"]
	data.append(headings)
	table_body = table.find('tbody')
	rows = table_body.find_all('tr')
	for row in rows:
	    cols = row.find_all('td')
	    cols = [ele.text.strip() for ele in cols]
	    data.append([ele for ele in cols[1:]])

	data = pd.DataFrame(data)
	data = data.rename(columns=data.iloc[0])
	data = data.reindex(data.index.drop(0))
	return data


def batting_leaders(season, league='all', qual='y', ind=0):
	soup = get_soup(start_season=season, end_season=season, league=league, qual=qual, ind=ind)
	table = get_table(soup)
	return table


#def get_batting_leaders_range(start_season, end_season, league='all', qual='y', ind=0):
#	pass
