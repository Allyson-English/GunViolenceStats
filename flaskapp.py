from flask import Flask, render_template
from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime

app = Flask(__name__)


@app.route("/")
def index():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }

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


if __name__ == "__main__":
    app.run(debug=True)
