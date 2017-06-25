import pandas as pd
import requests
import datetime
import io

# load in today's statcast data for your team of choice,
# and plot the strike zone for this game
def get_statcast(start_dt=None, end_dt=None, team=None):
	#pull data from baseball savant
	if start_dt or end_dt is None:
		today = datetime.datetime.today()
		start_dt = (today - datetime.timedelta(1)).strftime("%Y-%m-%d")
		end_dt = today.strftime("%Y-%m-%d")

	url = "https://baseballsavant.mlb.com/statcast_search/csv?all=true&hfPT=&hfAB=&hfBBT=&hfPR\
		=&hfZ=&stadium=&hfBBL=&hfNewZones=&hfGT=R%7CPO%7CS%7C=&hfSea=&hfSit=&player_type=\
		pitcher&hfOuts=&opponent=&pitcher_throws=&batter_stands=&hfSA=&game_date_gt={}&\
		game_date_lt={}&team=&position=&hfRO=&home_road=&hfFlag=&metric_1=&hfInn=&min_pitches\
		=0&min_results=0&group_by=name&sort_col=pitches&player_event_sort=h_launch_speed&\
		sort_order=desc&min_abs=0&type=details&".format(start_dt, end_dt)
	s=requests.get(url).content
	df = pd.read_csv(io.StringIO(s.decode('utf-8')))

	#select only pitches from a particular team
	valid_teams = ['MIN', 'PHI', 'BAL', 'NYY', 'LAD', 'OAK', 'SEA', 'TB', 'MIL', 'MIA',
       'KC', 'TEX', 'CHC', 'ATL', 'COL', 'HOU', 'CIN', 'LAA', 'DET', 'TOR',
       'PIT', 'NYM', 'CLE', 'CWS', 'STL', 'WSH', 'SF', 'SD', 'BOS'] #get a list
	if(team in valid_teams):
		df = df.loc[(df['home_team']==team)|(df['away_team']==team)]
	elif(team != None):
		print('Error: invalid team abbreviation. Valid team names are: {}'.format(valid_teams))
	return df

#data = get_statcast('2017-06-06', '2017-06-09', 'SEA')