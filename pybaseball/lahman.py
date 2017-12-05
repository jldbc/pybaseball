################################################
# WORK IN PROGRESS: ADD LAHMAN DB TO PYBASEBALL
# TODO: Make a callable function that retrieves the Lahman db
# Considerations: users should have a way to pull just the parts they want 
# within their code without having to write / save permanently. They should
# also have the option to write and save permanently if desired.  
################################################

import requests
import zipfile
import pandas as pd
from io import BytesIO, StringIO
from bs4 import BeautifulSoup

url = "http://seanlahman.com/files/database/baseballdatabank-2017.1.zip"
base_string = "baseballdatabank-2017.1/core/"

def get_lahman_zip():
	# Retrieve the Lahman database zip file. Making this a function since everything else
	# will be re-using these lines
	s=requests.get(url,stream=True)
	z = zipfile.ZipFile(BytesIO(s.content))
	return z

def download_lahman():
	# download entire lahman db to present working directory
	z = get_lahman_zip()
	z.extractall()

def lahman_parks():
	# do this for every table in the lahman db so they can exist as separate functions
	z = get_lahman_zip()
	f = base_string + "Parks.csv"
	data = pd.read_csv(z.open(f), header=0, sep=',', quotechar="'")
	return data


#df = lahman_parks()
#print(df.head())
#download_lahman()

