import requests
import pandas as pd
import sqlalchemy
from headers import db_path

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

test = create_tweet(engine, "New York", "this is a test")
