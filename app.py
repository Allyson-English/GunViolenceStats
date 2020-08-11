from headers import headers
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
    
    today_month = datetime.datetime.today()
    today_month = today_month.strftime('%B')

    today_date = datetime.datetime.today()
    today_date = int(today_date.strftime('%d'))

    today_year = datetime.datetime.today()
    today_year = today_year.strftime('%Y')

    yesterday_date = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_date = int(yesterday_date.strftime('%d'))

    yesterday_month = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_month = yesterday_month.strftime('%B')

    yesterday_year = datetime.datetime.today() - datetime.timedelta(days=1)
    yesterday_year = yesterday_year.strftime('%Y')

    today = f"{today_month} {today_date}, {today_year}"
    yesterday = f"{yesterday_month} {yesterday_date}, {yesterday_year}"
    
    db_path = db_path
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    
    with engine.connect() as conn:
        query = f"SELECT * FROM gun_violence WHERE date = '{today}' OR date = '{yesterday}';"
        df = pd.read_sql(query, conn)

    df = df.sort_values(by = 'date', ascending = False)

    df_len = len(df_len)

    df_len = len(df)
    deaths = df["killed"].sum()
    injuries = df["injured"].sum()
    states = len(df["state"].unique())
    x = datetime.datetime.now().strftime("%B %d, %Y")

    return render_template("index.html", df=df, df_len=df_len, x=x, deaths=deaths, injuries=injuries, states=states)


@app.route("/testing")
def testing():
    db_path = db_path
    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    with engine.connect() as conn:
        query1 = """SELECT * FROM gun_violence WHERE state = 'New York';"""
        dc_df = pd.read_sql(query1, conn)

    dc_df_len = len(dc_df)

    return render_template("testing.html", dc_df=dc_df, dc_df_len=dc_df_len)


if __name__ == "__main__":
    app.run(debug=True)
