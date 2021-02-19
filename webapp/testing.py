from headers import headers, db_path
import requests
import pandas as pd
import sqlite3
import sqlalchemy
from datetime import datetime
from sqlalchemy import Table, Column, Integer, String, MetaData


def makeconnection():
    now = datetime.now()
    print("Starting:", now)
    weblink = f'https://www.gunviolencearchive.org/last-72-hours'
    page = requests.get(weblink, headers=headers)
    page = page.text

    print("Ending:", datetime.now())


makeconnection()