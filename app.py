from headers import db_path
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

app = Flask(__name__)

@app.route("/")
def index():
    
    today = datetime.datetime.today()
    today_month = today.strftime('%B')
    today_date = int(today.strftime('%d'))
    today_year = today.strftime('%Y')

    yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_month = yesterday.strftime('%B')
    yesterday_date = int(yesterday.strftime('%d'))
    yesterday_year = yesterday.strftime('%Y')

    today = f"{today_month} {today_date}, {today_year}"
    yesterday = f"{yesterday_month} {yesterday_date}, {yesterday_year}"
    
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        query = f"""SELECT * FROM gun_violence
        WHERE date = '{today}' AND killed > 0 OR date = '{today}' AND injured > 0
        OR date = '{yesterday}' AND killed > 0 OR date = '{yesterday}' AND injured > 0
        GROUP BY state;"""
        df = pd.read_sql(query, conn)

    test = df.columns
    states = len(df)
    deaths = df["killed"].sum()
    injuries = df["injured"].sum()
    
    return render_template("index.html", df=df, states=states, today=today, deaths=deaths, injuries=injuries, test=test)


@app.route("/<state>")
def state_stats(state):

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    if f"{state}" == "NewYork":
        state = "New York"


    with engine.connect() as conn:
        query1 = f"""SELECT * FROM gun_violence WHERE state = '{state}';"""
        dc_df = pd.read_sql(query1, conn)


    dc_df_len = len(dc_df)

    return render_template("state_stats.html", dc_df=dc_df, dc_df_len=dc_df_len)


@app.route("/testing")
def testing():

    state_names = ["Alaska", 
    "Alabama", "Arkansas",
    "Arizona", "California", "Colorado", 
    "Connecticut", "District of Columbia", 
    "Delaware", "Florida", "Georgia", 
    "Hawaii", "Iowa", "Idaho", "Illinois", 
    "Indiana", "Kansas", "Kentucky", "Louisiana", 
    "Massachusetts", "Maryland", "Maine", "Michigan", 
    "Minnesota", "Missouri", "Mississippi", 
    "Montana", "North Carolina", "North Dakota", 
    "Nebraska", "New Hampshire", "New Jersey", 
    "New Mexico", "Nevada", "New York", "Ohio", 
    "Oklahoma", "Oregon", "Pennsylvania", "Puerto Rico", 
    "Rhode Island", "South Carolina", "South Dakota", 
    "Tennessee", "Texas", "Utah", "Virginia", "Vermont", 
    "Washington", "Wisconsin", "West Virginia", "Wyoming"]

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    with engine.connect() as conn:
        query1 = """SELECT * FROM gun_violence WHERE city = 'Washington';"""
        dc_df = pd.read_sql(query1, conn)

    dc_df_len = len(dc_df)

    return render_template("testing.html", dc_df=dc_df, dc_df_len=dc_df_len, state_names=state_names)


if __name__ == "__main__":
    app.run(debug=True)
