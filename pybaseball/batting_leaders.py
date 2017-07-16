import numpy as np
import pandas as pd
from bs4 import BeautifulSoup
import requests

# TODO: update url to include more stats 
def get_soup(start_season, end_season, league, qual, ind):
	url =  'http://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg={}&qual={}&type=c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,-1&season={}&month=0&season1={}&ind={}&team=&rost=&age=&filter=&players=&page=1_100000'
	#url = "http://www.fangraphs.com/leaders.aspx?pos=all&stats=pit&lg={}&qual={}&type=c,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,100,101,102,103,104,105,106,107,108,109,110,111,112,113,114,115,116,117,118,119,120,121,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,202,203,204,205,206,207,208,209,210,211,212,213,214,215,216,217,218,219,220,221,222,223,224,225,226,227,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,253,254,255,256,257,258,259,260,261,262,263,264,265,266,267,268,269,270,271,272,273,274,275,276,277,278,279,280,281,282,283,284,285,286,-1&season={}&month=0&season1={}&ind={}&team=&rost=&age=&filter=&players=&page=1_100000"
	url = url.format(league, qual, end_season, start_season, ind)
	s=requests.get(url).content
	#print(s)
	return BeautifulSoup(s, "html.parser")

def get_table(soup, ind):
	tables = soup.find_all('table')
	table = tables[10]
	data = []
	# couldn't find these in the table, hardcoding for now
	if ind == 0:
		headings = ["Name","Team","Age","G","AB","PA","H","1B","2B","3B","HR","R","RBI","BB","IBB","SO","HBP","SF","SH","GDP","SB","CS","AVG","GB","FB","LD","IFFB","Pitches","Balls","Strikes","IFH","BU","BUH","BB%","K%","BB/K","OBP","SLG","OPS","ISO","BABIP","GB/FB","LD%","GB%","FB%","IFFB%","HR/FB","IFH%","BUH%","wOBA","wRAA","wRC","Bat","Fld","Rep","Pos","RAR","WAR","Dol","Spd","wRC+","WPA","-WPA","+WPA","RE24","REW","pLI","phLI","PH","WPA/LI","Clutch","FB% (Pitch)","FBv","SL%","SLv","CT%","CTv","CB%","CBv","CH%","CHv","SF%","SFv","KN%","KNv","XX%","PO%","wFB","wSL","wCT","wCB","wCH","wSF","wKN","wFB/C","wSL/C","wCT/C","wCB/C","wCH/C","wSF/C","wKN/C","O-Swing%","Z-Swing%","Swing%","O-Contact%","Z-Contact%","Contact%","Zone%","F-Strike%","SwStr%","BsR","FA% (pfx)","FT% (pfx)","FC% (pfx)","FS% (pfx)","FO% (pfx)","SI% (pfx)","SL% (pfx)","CU% (pfx)","KC% (pfx)","EP% (pfx)","CH% (pfx)","SC% (pfx)","KN% (pfx)","UN% (pfx)","vFA (pfx)","vFT (pfx)","vFC (pfx)","vFS (pfx)","vFO (pfx)","vSI (pfx)","vSL (pfx)","vCU (pfx)","vKC (pfx)","vEP (pfx)","vCH (pfx)","vSC (pfx)","vKN (pfx)","FA-X (pfx)","FT-X (pfx)","FC-X (pfx)","FS-X (pfx)","FO-X (pfx)","SI-X (pfx)","SL-X (pfx)","CU-X (pfx)","KC-X (pfx)","EP-X (pfx)","CH-X (pfx)","SC-X (pfx)","KN-X (pfx)","FA-Z (pfx)","FT-Z (pfx)","FC-Z (pfx)","FS-Z (pfx)","FO-Z (pfx)","SI-Z (pfx)","SL-Z (pfx)","CU-Z (pfx)","KC-Z (pfx)","EP-Z (pfx)","CH-Z (pfx)","SC-Z (pfx)","KN-Z (pfx)","wFA (pfx)","wFT (pfx)","wFC (pfx)","wFS (pfx)","wFO (pfx)","wSI (pfx)","wSL (pfx)","wCU (pfx)","wKC (pfx)","wEP (pfx)","wCH (pfx)","wSC (pfx)","wKN (pfx)","wFA/C (pfx)","wFT/C (pfx)","wFC/C (pfx)","wFS/C (pfx)","wFO/C (pfx)","wSI/C (pfx)","wSL/C (pfx)","wCU/C (pfx)","wKC/C (pfx)","wEP/C (pfx)","wCH/C (pfx)","wSC/C (pfx)","wKN/C (pfx)","O-Swing% (pfx)","Z-Swing% (pfx)","Swing% (pfx)","O-Contact% (pfx)","Z-Contact% (pfx)","Contact% (pfx)","Zone% (pfx)","Pace","Def","wSB","UBR","Age Rng","Off","Lg","wGDP","Pull%","Cent%","Oppo%","Soft%","Med%","Hard%","TTO%","CH% (pi)","CS% (pi)","CU% (pi)","FA% (pi)","FC% (pi)","FS% (pi)","KN% (pi)","SB% (pi)","SI% (pi)","SL% (pi)","XX% (pi)","vCH (pi)","vCS (pi)","vCU (pi)","vFA (pi)","vFC (pi)","vFS (pi)","vKN (pi)","vSB (pi)","vSI (pi)","vSL (pi)","vXX (pi)","CH-X (pi)","CS-X (pi)","CU-X (pi)","FA-X (pi)","FC-X (pi)","FS-X (pi)","KN-X (pi)","SB-X (pi)","SI-X (pi)","SL-X (pi)","XX-X (pi)","CH-Z (pi)","CS-Z (pi)","CU-Z (pi)","FA-Z (pi)","FC-Z (pi)","FS-Z (pi)","KN-Z (pi)","SB-Z (pi)","SI-Z (pi)","SL-Z (pi)","XX-Z (pi)","wCH (pi)","wCS (pi)","wCU (pi)","wFA (pi)","wFC (pi)","wFS (pi)","wKN (pi)","wSB (pi)","wSI (pi)","wSL (pi)","wXX (pi)","wCH/C (pi)","wCS/C (pi)","wCU/C (pi)","wFA/C (pi)","wFC/C (pi)","wFS/C (pi)","wKN/C (pi)","wSB/C (pi)","wSI/C (pi)","wSL/C (pi)","wXX/C (pi)","O-Swing% (pi)","Z-Swing% (pi)","Swing% (pi)","O-Contact% (pi)","Z-Contact% (pi)","Contact% (pi)","Zone% (pi)","Pace (pi)"]
	else:
		headings = ["Season","Name","Team","Age","G","AB","PA","H","1B","2B","3B","HR","R","RBI","BB","IBB","SO","HBP","SF","SH","GDP","SB","CS","AVG","GB","FB","LD","IFFB","Pitches","Balls","Strikes","IFH","BU","BUH","BB%","K%","BB/K","OBP","SLG","OPS","ISO","BABIP","GB/FB","LD%","GB%","FB%","IFFB%","HR/FB","IFH%","BUH%","wOBA","wRAA","wRC","Bat","Fld","Rep","Pos","RAR","WAR","Dol","Spd","wRC+","WPA","-WPA","+WPA","RE24","REW","pLI","phLI","PH","WPA/LI","Clutch","FB% (Pitch)","FBv","SL%","SLv","CT%","CTv","CB%","CBv","CH%","CHv","SF%","SFv","KN%","KNv","XX%","PO%","wFB","wSL","wCT","wCB","wCH","wSF","wKN","wFB/C","wSL/C","wCT/C","wCB/C","wCH/C","wSF/C","wKN/C","O-Swing%","Z-Swing%","Swing%","O-Contact%","Z-Contact%","Contact%","Zone%","F-Strike%","SwStr%","BsR","FA% (pfx)","FT% (pfx)","FC% (pfx)","FS% (pfx)","FO% (pfx)","SI% (pfx)","SL% (pfx)","CU% (pfx)","KC% (pfx)","EP% (pfx)","CH% (pfx)","SC% (pfx)","KN% (pfx)","UN% (pfx)","vFA (pfx)","vFT (pfx)","vFC (pfx)","vFS (pfx)","vFO (pfx)","vSI (pfx)","vSL (pfx)","vCU (pfx)","vKC (pfx)","vEP (pfx)","vCH (pfx)","vSC (pfx)","vKN (pfx)","FA-X (pfx)","FT-X (pfx)","FC-X (pfx)","FS-X (pfx)","FO-X (pfx)","SI-X (pfx)","SL-X (pfx)","CU-X (pfx)","KC-X (pfx)","EP-X (pfx)","CH-X (pfx)","SC-X (pfx)","KN-X (pfx)","FA-Z (pfx)","FT-Z (pfx)","FC-Z (pfx)","FS-Z (pfx)","FO-Z (pfx)","SI-Z (pfx)","SL-Z (pfx)","CU-Z (pfx)","KC-Z (pfx)","EP-Z (pfx)","CH-Z (pfx)","SC-Z (pfx)","KN-Z (pfx)","wFA (pfx)","wFT (pfx)","wFC (pfx)","wFS (pfx)","wFO (pfx)","wSI (pfx)","wSL (pfx)","wCU (pfx)","wKC (pfx)","wEP (pfx)","wCH (pfx)","wSC (pfx)","wKN (pfx)","wFA/C (pfx)","wFT/C (pfx)","wFC/C (pfx)","wFS/C (pfx)","wFO/C (pfx)","wSI/C (pfx)","wSL/C (pfx)","wCU/C (pfx)","wKC/C (pfx)","wEP/C (pfx)","wCH/C (pfx)","wSC/C (pfx)","wKN/C (pfx)","O-Swing% (pfx)","Z-Swing% (pfx)","Swing% (pfx)","O-Contact% (pfx)","Z-Contact% (pfx)","Contact% (pfx)","Zone% (pfx)","Pace","Def","wSB","UBR","Age Rng","Off","Lg","wGDP","Pull%","Cent%","Oppo%","Soft%","Med%","Hard%","TTO%","CH% (pi)","CS% (pi)","CU% (pi)","FA% (pi)","FC% (pi)","FS% (pi)","KN% (pi)","SB% (pi)","SI% (pi)","SL% (pi)","XX% (pi)","vCH (pi)","vCS (pi)","vCU (pi)","vFA (pi)","vFC (pi)","vFS (pi)","vKN (pi)","vSB (pi)","vSI (pi)","vSL (pi)","vXX (pi)","CH-X (pi)","CS-X (pi)","CU-X (pi)","FA-X (pi)","FC-X (pi)","FS-X (pi)","KN-X (pi)","SB-X (pi)","SI-X (pi)","SL-X (pi)","XX-X (pi)","CH-Z (pi)","CS-Z (pi)","CU-Z (pi)","FA-Z (pi)","FC-Z (pi)","FS-Z (pi)","KN-Z (pi)","SB-Z (pi)","SI-Z (pi)","SL-Z (pi)","XX-Z (pi)","wCH (pi)","wCS (pi)","wCU (pi)","wFA (pi)","wFC (pi)","wFS (pi)","wKN (pi)","wSB (pi)","wSI (pi)","wSL (pi)","wXX (pi)","wCH/C (pi)","wCS/C (pi)","wCU/C (pi)","wFA/C (pi)","wFC/C (pi)","wFS/C (pi)","wKN/C (pi)","wSB/C (pi)","wSI/C (pi)","wSL/C (pi)","wXX/C (pi)","O-Swing% (pi)","Z-Swing% (pi)","Swing% (pi)","O-Contact% (pi)","Z-Contact% (pi)","Contact% (pi)","Zone% (pi)","Pace (pi)"]

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

	#replace empty strings with NaN
	data.replace(r'^\s*$', np.nan, regex=True, inplace = True)

	# convert percentage strings to floats   FB% duplicated
	percentages = ['Zone% (pi)','Contact% (pi)','Z-Contact% (pi)','O-Contact% (pi)','Swing% (pi)','Z-Swing% (pi)','O-Swing% (pi)','XX% (pi)','SL% (pi)','SI% (pi)','SB% (pi)','KN% (pi)','FS% (pi)','FC% (pi)','FA% (pi)','CU% (pi)','CS% (pi)','CH% (pi)','TTO%','Hard%','Med%','Soft%','Oppo%','Cent%','Pull%','Zone% (pfx)','Contact% (pfx)','Z-Contact% (pfx)','O-Contact% (pfx)','Swing% (pfx)','Z-Swing% (pfx)','O-Swing% (pfx)','UN% (pfx)','KN% (pfx)','SC% (pfx)','CH% (pfx)','EP% (pfx)','KC% (pfx)','CU% (pfx)','SL% (pfx)','SI% (pfx)','FO% (pfx)','FS% (pfx)','FC% (pfx)','FT% (pfx)','FA% (pfx)','SwStr%','F-Strike%','Zone%','Contact%','Z-Contact%','O-Contact%','Swing%','Z-Swing%','O-Swing%','PO%','XX%','KN%','SF%','CH%','CB%','CT%','SL%','FB%','BUH%','IFH%','HR/FB','IFFB%','FB% (Pitch)','GB%', 'LD%','GB/FB','K%','BB%']
	for col in percentages:
		# skip if column is all NA (happens for some of the more obscure stats + in older seasons)
		if data[col].count()>0:
			data[col] = data[col].str.strip(' %')
			data[col] = data[col].str.strip('%')
			data[col] = data[col].astype(float)/100.
		else:
			#print(col)
			pass

	#convert everything except name and team to numeric (Dol?)
	cols_to_numeric = [col for col in data.columns if col not in ['Name', 'Team', 'Age Rng', 'Dol']]
	data[cols_to_numeric] = data[cols_to_numeric].astype(float)

	#sort by WAR and OPS so best players float to the top
	data = data.sort_values(['WAR', 'OPS'], ascending=False)
	return data

def batting_stats(start_season, end_season=None, league='all', qual='y', ind=1):
	if start_season is None:
		raise ValueError("You need to provide at least one season to collect data for. Try pitching_leaders(season) or pitching_leaders(start_season, end_season).")
	if end_season is None:
		end_season = start_season
	soup = get_soup(start_season=start_season, end_season=end_season, league=league, qual=qual, ind=ind)
	table = get_table(soup, ind)
	return table

