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

twitter_statement = f"In the past 24 hours, across {states_count} states, there have been {deaths} deaths and {injuries} injuries attributed to gun violence in the United States."
# api.update_status(twitter_statement)

for state in states_names:
    temp = df[df.state == state]
    if temp.killed.sum() > 3 and temp.injured.sum() > 3:
        daily_statement = f"In the past day alone, there have been {temp.killed.sum()} deaths and {temp.injured.sum()} injuries due to gun violence in {state}. What are {state} lawmakers doing to curb there epidemic of gun violence in our country and in their home state?"
        api.update_status(daily_statement)
    
    elif temp.killed.sum() > 2 and temp.injured.sum() <= 1:
        daily_statement = f"There have been {temp.killed.sum()} lives lost to gun violence in {state} in the past 24 hours alone. What are {state} lawmakers doing to keep their citizens safe?"
        api.update_status(daily_statement)
    
week_of_data = pd.DataFrame()


with engine.connect() as conn:
    for num in range(7):
        temp_day = datetime.now(tz=DC_tz)
        temp_day = temp_day - timedelta(days=7)

        temp_month = temp_day.strftime('%B')
        temp_date = int(temp_day.strftime('%d'))
        temp_year = temp_day.strftime('%Y')
        
        temp_full = f"{temp_month} {temp_date}, {temp_year}"
        
        query = f"""SELECT * FROM gun_violence
            WHERE date = '{temp_full}' AND killed > 0 OR date = '{temp_full}' AND injured > 0
            GROUP BY state;"""
        
        df = pd.read_sql(query, conn)
        
        week_of_data = week_of_data.append(df)
        
last_week_statement = f"Across the United States, there have been {week_of_data.killed.sum()} deaths and {week_of_data.injured.sum()} injuries due to gun violence in the past week. America needs sensible gun policy now."
api.update_status(last_week_statement)

for state in states_names:
    temp = week_of_data[week_of_data.state == state]
    if temp.killed.sum() >= 10:
        statement = f"In the past week, {temp.killed.sum()} individuals were killed as a result of gun violence in {state}. {state} representatives can and must do  more to prevent future gun violence in their home state, and across our country."
        api.update_status(statement)
        
    if temp.injured.sum() >= 10:
        statement = f"In {state}, {temp.injured.sum()} individuals sustained injuries as a result of firearms over the last week."
        api.update_status(statement)