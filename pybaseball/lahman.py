################################################
# WORK IN PROGRESS: ADD LAHMAN DB TO PYBASEBALL
# TODO: Make a callable function that retrieves the Lahman db
# Considerations: users should have a way to pull just the parts they want 
# within their code without having to write / save permanently. They should
# also have the option to write and save permanently if desired.  
################################################

import requests
import zipfile
from io import BytesIO
from bs4 import BeautifulSoup

# Download zip file and extract all files into working directory
url = "http://seanlahman.com/files/database/baseballdatabank-2017.1.zip"
s=requests.get(url,stream=True)
z = zipfile.ZipFile(BytesIO(s.content))
z.extractall()
