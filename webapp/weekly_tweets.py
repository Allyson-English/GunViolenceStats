import tweepy
from datetime import datetime, timedelta
from dateutil import tz
import sqlalchemy
import pandas as pd
from sqlalchemy import Table, Column, Integer, String, MetaData
from headers import twitter_api_key, twitter_api_key_secret, twitter_access_token, twitter_token_secret, db_path

# establish connection to twitter
auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
auth.set_access_token(twitter_access_token, twitter_token_secret)
api = tweepy.API(auth)

# establish correct day and timezone
DC_tz = tz.gettz("US/Eastern")

# initiate connection to database
engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

# instantiate empty table, to be updated in loop below
week_of_data = pd.DataFrame()

state_names = []

# read data out of db into empty table above
with engine.connect() as conn:
    
    # data for past seven days 
    for num in range(7):
        temp_day = datetime.now(tz=DC_tz)
        temp_day = temp_day - timedelta(days=num)

        temp_month = temp_day.strftime('%B')
        temp_date = int(temp_day.strftime('%d'))
        temp_year = temp_day.strftime('%Y')
        
        temp_full = f"{temp_month} {temp_date}, {temp_year}"
        
        query = f"""SELECT * FROM gun_violence
            WHERE day = '{temp_date}' AND month = '{temp_month}' AND year = '{temp_year}' AND killed > 0 
            OR day = '{temp_date}' AND month = '{temp_month}' AND year = '{temp_year}' AND injured > 0 
            GROUP BY state;"""
        
        df = pd.read_sql(query, conn)
        
        state_names.extend(df["state"])
        
        week_of_data = week_of_data.append(df)
  
# broad statement about gun violence rates in America
last_week_statement = f"In the  past week, across the United States, there have been {week_of_data.killed.sum()} deaths and {week_of_data.injured.sum()} injuries due to gun violence. America needs sensible gun policy now."

# look at each state for any particularly large numbers that should be reported
for state in state_names:
    print(state)
    temp = week_of_data[week_of_data.state == state]
    if temp.killed.sum() >= 10:
        
        if temp.injured.sum() >= 3:
            statement = f"In the past week, {temp.killed.sum()} individuals were killed and {temp.injured.sum()} individuals were injured as a result of gun violence in {state}. {state} representatives can and must do  more to prevent future gun violence in their home state, and across our country."
            api.update_status(statement)
            
        else:
            statement = f"In the past week, {temp.killed.sum()} individuals were killed as a result of gun violence in {state}. {state} representatives can and must do  more to prevent future gun violence in their home state, and across our country."
            api.update_status(statement)
        
    if temp.injured.sum() >= 5 and not temp.killed.sum() >= 10:
        statement = f"In {state}, {temp.injured.sum()} individuals sustained injuries as a result of firearms over the last week. What are {state} policymakers doing to enact sensible gun policy?"
        api.update_status(statement)
        
api.update_status(last_week_statement)