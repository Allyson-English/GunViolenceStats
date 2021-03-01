import requests
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
import sqlite3
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData, inspect
from headers import db_path


# website listing current twitter information for all US reps
url = "https://triagecancer.org/congressional-social-media"

# read data off of site in form of table
site = requests.get(url).text
representative_data = pd.read_html(site)[0]

# select relevant columns
twitter_data = representative_data[['State', 'Member of Congress', 'Name', 'Twitter']]




def clean_states(x):
    drop_terms = ['29th', '8th', '44th', '35th', '47th', '2nd', '25th', '43rd', '15th', '10th', '26th', '33rd', '5th', '18th', '9th', '11th', '27th', '1st', '19th', '46th', '17th', '38th', '49th', '6th', '31st', '41st', '48th', '50th', '7th', '21st', '34th', '3rd', '22nd', '20th', '24th', '16th', '23rd', '30th', '37th', 'Division', '51st', '32nd', '28th', '4th', '42nd', 'District', '40th', '13th', '53rd', '52nd', '36th', '39th', '14th', '45th', 'At-Large', '12th']

    if "District of Columbia" in x:
        return "District of Columbia"
    
    x = x.split()
    x = [ea for ea in x if ea not in drop_terms]
    return " ".join(x)

twitter_data['State'] = twitter_data['State'].apply(lambda x: clean_states(x))
twitter_data['Title'] = twitter_data['Member of Congress'].apply(lambda x: x.split()[-1])
twitter_data['LNAME'] = twitter_data['Name'].apply(lambda x: x.split()[0].replace(",",""))
twitter_data['FullTitle'] = twitter_data['Title']+" " +twitter_data['LNAME']

# drop columns used to transform data
twitter_data = twitter_data.drop(columns=['LNAME', 'Title'])


engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')
    
# Establish connection to table 
metadata = MetaData()
twitter_handles = Table('twitter_handles', metadata, autoload = True, autoload_with = engine)
metadata.create_all(engine)
# print(metadata.tables)

# for i in range(len(twitter_data)):
#     indx = i + 1
#     state_temp = twitter_data['State'][i]
#     office_temp = twitter_data['Member of Congress'][i]
#     name_temp = twitter_data['Name'][i]
#     twitter_handle_temp = twitter_data['Twitter'][i]
#     title_temp = twitter_data['FullTitle'][i]
#     #print(state, office, name, twitter, title)
# 
#     insert = twitter_handles.insert().values(index = indx,
#                                     state = state_temp, 
#                                    office = office_temp, 
#                                    name = name_temp, 
#                                    handle = twitter_handle_temp, 
#                                    title = title_temp)
# 
#     with engine.connect() as conn:
#         conn.execute(insert)

with engine.connect() as conn:
    query = "SELECT * FROM twitter_handles LIMIT 3;"
    df = pd.read_sql(query, conn)
    
print(df.head)