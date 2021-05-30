import tweepy
from datetime import datetime, timedelta
from dateutil import tz
import sqlalchemy
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, MetaData
from headers import twitter_api_key, twitter_api_key_secret, twitter_access_token, twitter_token_secret, db_path

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
auth.set_access_token(twitter_access_token, twitter_token_secret)

api = tweepy.API(auth)

DC_tz = tz.gettz("US/Eastern")
today = datetime.now(tz=DC_tz)

today_month = today.strftime('%B')
today_date = int(today.strftime('%d'))
today_year = today.strftime('%Y')

yesterday = today - timedelta(days=1)
yesterday_month = yesterday.strftime('%B')
yesterday_date = int(yesterday.strftime('%d'))
yesterday_year = yesterday.strftime('%Y')

lastweek = today - timedelta(days=7)

lastweek_month = lastweek.strftime('%B')
lastweek_date = int(lastweek.strftime('%d'))
lastweek_year = lastweek.strftime('%Y')

today = f"{today_month} {today_date}, {today_year}"
yesterday = f"{yesterday_month} {yesterday_date}, {yesterday_year}"

engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

with engine.connect() as conn:
    query = f"""SELECT * FROM gun_violence
    WHERE date = '{today}' AND killed > 0 OR date = '{today}' AND injured > 0
    OR date = '{yesterday}' AND killed > 0 OR date = '{yesterday}' AND injured > 0
    GROUP BY state;"""
    df = pd.read_sql(query, conn)

states_count = len(df)
states_names = df["state"].unique()
deaths = df["killed"].sum()
injuries = df["injured"].sum()

# make sure it will be singular if there is only one death/ injury

twitter_statement = f"In the last 24 hours, across {states_count} US states, there have been {deaths} deaths and {injuries} injuries attributed to gun violence."
api.update_status(twitter_statement)

for state in states_names:
    temp = df[df.state == state]
    
    if temp.killed.sum() >= 3:
        
        if temp.injured.sum() > 2:
            daily_statement = f"In the past 24 hours, there have been {temp.killed.sum()} deaths and {temp.injured.sum()} injuries due to gun violence in {state}. What are {state} lawmakers doing to curb there epidemic of gun violence in our country and in their home state?"
            api.update_status(daily_statement)
        
        else:
            daily_statement = f"In the past 24 hours, there have been {temp.killed.sum()} deaths due to gun violence in {state}. What are {state} lawmakers doing to curb there epidemic of gun violence in our country and in their home state?"
            api.update_status(daily_statement)
        
    if temp.injured.sum() >= 5:
        
        if temp.killed.sum() < 3:
            
            daily_statement = f"In the past 24 hours, {temp.injured.sum()} individuals in {state} have sustained injuried due to gun violence."
            api.update_status(daily_statement)
            
            
    
