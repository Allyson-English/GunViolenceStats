from headers import headers, db_path
import requests
import pandas as pd
import sqlite3
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

from bs4 import BeautifulSoup

import time
import re

web_path = 'https://www.gunviolencearchive.org/last-72-hours?page={}'.format()

data = requests.get(web_path, headers=headers)

soup = BeautifulSoup(data.text)

table = soup.find_all("tr", {"class":"odd"}) + soup.find_all("tr", {"class":"even"})

pagenums = soup.find_all("li", {"class":"pager-item"})

for i in pagenums:
    
    num = re.search('>\d{1}<', str(i))
    
    if num:
        
        num = num.group().replace(">","").replace("<","")
        
        print(num)

table = [str(x) for x in table]

data = []

for i in table:
    
    row = str(i)
    
    row = row.split("<td>")
    
    tbl = []
    
    for item in row:
        
        drop_characters = re.search('<(.*\w*?)>', item)
        
        if drop_characters:
            
            item = item.replace(drop_characters.group(), "")
            
            if item:
            
                tbl.append(item)
            
    data.append(tbl)
    
colnames = ['date', 'state', 'city', 'address', 'killed', 'injured']

df = pd.DataFrame(data, columns =colnames) 
df 
