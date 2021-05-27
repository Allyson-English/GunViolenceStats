from headers import db_path
from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime, timedelta
from dateutil import tz
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

import json
import plotly
import plotly.express as px
from IPython.display import Image

app = Flask(__name__)

@app.route("/")
def index():
    
    DC_tz = tz.gettz("US/Eastern")
    today = datetime.now(tz=DC_tz)
    
    today_month = today.strftime('%B')
    today_date = int(today.strftime('%d'))
    today_year = today.strftime('%Y')

    yesterday = today - timedelta(days=1)
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

    states_count = len(df)
    states_names = df["state"].unique()
    deaths = df["killed"].sum()
    injuries = df["injured"].sum()
    
    twitter_statement = f"https://www.twitter.com/intent/tweet?url=In the past 24 hours, across {states_count} states, there have been {deaths} deaths and {injuries} injuries attributed to gun violence in the United States. Track daily incidence of gun violence @ZeroDaysLive"
    
    return render_template("index.html", df=df, states_count=states_count, states_names=states_names,
                           today=today, deaths=deaths, injuries=injuries, twitter_statement=twitter_statement)


@app.route("/<state>")
def state_stats(state):

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")


    with engine.connect() as conn:
        query1 = f"""SELECT * FROM gun_violence WHERE state IN
                    (SELECT state from state_names WHERE abbreviations = '{state}');"""
        dc_df = pd.read_sql(query1, conn)


    dc_df_len = len(dc_df)

    return render_template("state_stats.html", dc_df=dc_df, dc_df_len=dc_df_len)



if __name__ == "__main__":
    app.run(debug=True)
