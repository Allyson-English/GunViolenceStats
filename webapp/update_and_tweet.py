from headers import twitter_api_key, twitter_api_key_secret, twitter_access_token, twitter_token_secret, db_path
import requests
import pandas as pd
import sqlite3
import sqlalchemy
from updateDB import update_table
from sqlalchemy import Table, Column, Integer, String, MetaData

# establish connection to twitter

auth = tweepy.OAuthHandler(twitter_api_key, twitter_api_key_secret)
auth.set_access_token(twitter_access_token, twitter_token_secret)

api = tweepy.API(auth)

update_table(db_path)