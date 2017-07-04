import pandas as pd
import requests
import datetime
import warnings
import io

def validate_datestring(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def sanitize_input(start_dt, end_dt):
	# if no dates are supplied, assume they want yesterday's data
	# send a warning in case they wanted to specify
	if start_dt is None and end_dt is None:
		today = datetime.datetime.today()
		start_dt = (today - datetime.timedelta(1)).strftime("%Y-%m-%d")
		end_dt = today.strftime("%Y-%m-%d")

		print("Warning: no date range supplied. Returning yesterday's Statcast data. For a different date range, try get_statcast(start_dt, end_dt).")

	#if only one date is supplied, assume they only want that day's stats
	#query in this case is from date 1 to date 1
	if start_dt is None:
		start_dt = end_dt
	if end_dt is None:
		end_dt = start_dt

	# now that both dates are not None, make sure they are valid date strings
	validate_datestring(start_dt)
	validate_datestring(end_dt)
	return start_dt, end_dt

def statcast(start_dt=None, end_dt=None, team=None):
	""" 
	Pulls statcast data from Baseball Savant.
	"""
	start_dt, end_dt = sanitize_input(start_dt, end_dt)


	# inputs are valid if either both or zero dates are supplied. Not valid of only one given.
	if start_dt and end_dt:
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
			raise ValueError('Error: invalid team abbreviation. Valid team names are: {}'.format(valid_teams))
		return df
