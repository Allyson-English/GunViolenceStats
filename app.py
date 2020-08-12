from headers import db_path
from flask import Flask, render_template
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

if False:
    headers = headers

    url = "https://www.gunviolencearchive.org/last-72-hours"

    page = requests.get(url, headers=headers)
    page = page.text

    df = pd.read_html(page, header=0, index_col=0)
    df = df[0].reset_index().drop(columns=["Operations"])
    df.columns = ["date", "state", "city", "address", "killed", "injured"]

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
        query = f"SELECT * FROM gun_violence WHERE city = 'Washington' AND date = '{today}' OR city = 'Washington' AND date = '{yesterday}';"
        df = pd.read_sql(query, conn)

    df = df.sort_values(by = 'state', ascending=True)

    df_len = len(df)
    deaths = df["killed"].sum()
    injuries = df["injured"].sum()
    states = len(df["state"].unique())

    return render_template("index.html", df=df, df_len=df_len, today=today, deaths=deaths, injuries=injuries, states=states)


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
        query1 = """SELECT * FROM gun_violence WHERE state = 'New York';"""
        dc_df = pd.read_sql(query1, conn)

    dc_df_len = len(dc_df)

    return render_template("testing.html", dc_df=dc_df, dc_df_len=dc_df_len, state_names=state_names)


if __name__ == "__main__":
    app.run(debug=True)
