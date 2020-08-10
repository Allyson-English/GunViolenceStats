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
    headers = headers

    url = "https://www.gunviolencearchive.org/last-72-hours"

    page = requests.get(url, headers=headers)
    page = page.text

    df = pd.read_html(page, header=0, index_col=0)
    df = df[0].reset_index().drop(columns=["Operations"])
    df.columns = ["date", "state", "city", "address", "killed", "injured"]

    for i in range(0, len(df)):
        if df["killed"][i] == 0 and df["injured"][i] == 0:
            df = df.drop([i])

    df = df.reset_index()
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
