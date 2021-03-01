import requests
import pandas as pd
import sqlalchemy
from headers import db_path
import sqlite3
from datetime import datetime, timedelta
from dateutil import tz
import tweet_generator 
from sqlalchemy import Table, Column, Integer, String, MetaData

engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

def create_tweet(engine, state, statement):
    
    tweets = []
    
    with engine.connect() as conn:
        query = f"SELECT handle, title FROM twitter_handles WHERE state = '{state}';"
        df = pd.read_sql(query, conn)
        

    state_rep_dict = dict(df.T)

    for k, v in state_rep_dict.items():
        
        if v['handle'] == None:
            pass
        
        else:
            t = f"{v['handle']} {v['title']} {statement}"
            tweets.append(t)
    
    return tweets

def lastweek_stats():
    
    tweets_all_states = []

    # Establish path to dataabase and make connection to sql engine
    path = db_path
    engine = sqlalchemy.create_engine(f'sqlite:///{path}')

    # Establish connection to table 
    metadata = MetaData()
    gun_violence = Table('gun_violence', metadata, autoload = True, autoload_with = engine)
    metadata.create_all(engine)
     
    # Extra currennt date
    DC_tz = tz.gettz("US/Eastern")
    today = datetime.now(tz=DC_tz)

    # Determine date exactly one week ago
    week_prior = (today - timedelta(days=7))
    #today = today.strftime('%B %d %Y')

    # create list of all dates in the past week
    daterange = pd.date_range(week_prior, today).tolist()
        
    # create dictionary to hold data by day for past week
    holder_dict = {}


    for each_day in daterange:
        
        # select and format each date
        each_day = each_day.strftime('%B %d %Y')
        each_day = each_day[:-5] + "," + each_day[-5:]
        
        # read data out of database for that date
        with engine.connect() as conn:
            query1 = f"""SELECT * FROM gun_violence WHERE date = '{each_day}'"""
            df1 = pd.read_sql(query1, conn)
            
            # group data by state and transform into dictionary
            holder = dict(df1.groupby(by='state').sum()[['killed', 'injured']].T)
            
            # iterate through dataframe dictionary to add information to holder dictionary
            for k, v in holder.items():
                if k in holder_dict.keys():
                    if v['killed'] > 0:
                        holder_dict[k]['killed'] = v['killed']
                    if v['injured'] > 0:
                        holder_dict[k]['injured'] = v['injured']
                else:
                    temp = {}
                    if v['killed'] > 0:
                        temp['killed'] = v['killed']
                    if v['injured'] > 0:
                        temp['injured'] = v['injured']
                    if len(temp.keys()) > 0:
                        holder_dict[k] = temp
                
    # for each item in holder dictionary
    for k, v in holder_dict.items():
        
        state = k
        
        if v.get("injured"):
            if v['injured'] > 1:
                injured = f"{v['injured']} injuires"
            if v['injured'] == 1:
                injured = f"{v['injured']} injuiry"
        
        if v.get("killed"):
            if v['killed'] > 1:
                fatality = f"there have been {v['killed']} deaths"
            if v['killed'] == 1:
                fatality = f"there has been {v['killed']} death"
        
        if fatality and injured:
            statement = f"in the past week, {fatality} and {injured} attributed to gun violence in your state. What are you doing to prevent future gun violence in {state}?"
        
        if fatality and not injured:
            statement = f"in the past week, {fatality} attributed to gun violence in your state. What are you doing to prevent future gun violence in {state}?"
            
        if not fatality and injured:
            if v['injured'] > 1:
                statement = f"in the past week, there have been {injured} attributed to gun violence in your state. What are you doing to prevent future gun violence in {state}?"
            if v['injured'] == 1:
                statement = f"in the past week, there has been {injured} attributed to gun violence in your state. What are you doing to prevent future gun violence in {state}?"
        if state == 'District of Columbia':
            statement = statement.replace("in your state", "in your city").replace("in District", "in the District")
            
        
        tweets_by_state = create_tweet(engine, state, statement)
        
        for ea in tweets_by_state:
            tweets_all_states.append(ea)

    return tweets_all_states
