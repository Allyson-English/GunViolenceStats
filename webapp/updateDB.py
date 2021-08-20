from headers import headers, twitter_api_key, twitter_api_key_secret, twitter_access_token, twitter_token_secret, db_path
import tweepy
from datetime import datetime
import requests
import pandas as pd
import sqlite3
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

### Update Table Function
def grab_new_data(db_pathway, page_number = 14):

    # Scrape data from website
    print("starting scrape")

    new_data = pd.DataFrame()
    
    for i in range(0, page_number):
        
        weblink = f"https://www.gunviolencearchive.org/last-72-hours?page={i}"
        page = requests.get(weblink, headers=headers)
        page = page.text
        
        # Use pandas read_html function to pull the current table from the website 
        df = pd.read_html(page, header=0, index_col=0)
        df = df[0].reset_index().drop(columns = ['Operations'])
        df.columns = ['date', 'state', 'city', 'address', 'killed', 'injured']
        
        df['day'] = df['date'].apply(lambda x: int(x.split()[1].replace(" ","").replace(",","")))
        df['month'] = df['date'].apply(lambda x: x.split()[0].replace(" ","").replace(",",""))
        df['year'] = df['date'].apply(lambda x: int(x.split()[-1].replace(" ","").replace(",","")))
        df['date'] = pd.to_datetime(df['date'])

        df = df[['date', 'day', 'month', 'year', 'state', 'city', 'address', 'killed', 'injured']]
        
        new_data = new_data.append(df)

    return new_data.drop_duplicates().reset_index(drop=True)

def import_data(df):

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")
    with engine.connect() as conn:
        query = f"""SELECT MAX(entry) FROM gun_violence;"""
        max = pd.read_sql(query, conn).iloc[0][0]
        if not max:
            max = 0
    n_entry = 1

    for i in range(len(df)):
        
        clean_entrynum = int(n_entry+max)
        clean_date = str(df['date'][i]).split()[0]
        clean_day = int(df['day'][i])
        clean_month = str(df['month'][i])
        clean_year = int(df['year'][i])
        clean_state = str(df['state'][i])
        
        clean_city = str(df['city'][i])
        clean_city = clean_city.replace("(","").replace(",","").replace("'","").replace(")","")
        
        clean_addr = str(df['address'][i])
        clean_addr = clean_addr.replace("(","").replace(",","").replace("'","").replace(")","")
        
        clean_killed = int(df['killed'][i])
        clean_injured = int(df['injured'][i])

        if clean_killed >= 4:
            clean_ms = True
        if not clean_killed == 5:
            clean_ms = False

        evaluate_entry(db_path, clean_entrynum, clean_date, clean_day, clean_month, clean_year, clean_state, clean_city, clean_addr, clean_killed, clean_injured, clean_ms)
        n_entry += 1
       
### If duplicate date exists, delete 
def delete_duplicate(db_pathway, clean_date, clean_state, clean_city, clean_addr, clean_killed, clean_injured):
    
    sqliteConnection = sqlite3.connect(db_pathway)

    try:
        cursor = sqliteConnection.cursor()

        del_statement = f"""DELETE FROM gun_violence 
                            WHERE date = '{clean_date}' 
                            AND state = '{clean_state}' 
                            AND city = '{clean_city}'
                            AND address = '{clean_addr}'
                            AND killed = '{clean_killed}'
                            AND injured = '{clean_injured}';"""
        cursor.execute(del_statement)
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
    
### After ensuring the row will not be a duplicate, add new row 
def add_row(metadata, db, engine, clean_entrynum, clean_date, clean_day, clean_month, clean_year, clean_state, clean_city, clean_addr, clean_killed, clean_injured, clean_ms):

    metadata.create_all(engine)
    
    ins = db.insert().values(
                                entry = clean_entrynum,
                                date = datetime.strptime(clean_date, '%Y-%m-%d'),
                                day = clean_day,
                                month = clean_month,
                                year = clean_year,
                                state = clean_state,
                                city = clean_city,
                                address = clean_addr,
                                killed = clean_killed,
                                injured = clean_injured,
                                mass_shooting = clean_ms
                                   )

    with engine.connect() as conn:
        conn.execute(ins)
    
    
### Insert Rows SQL Function
def evaluate_entry(db_pathway, clean_entrynum, clean_date, clean_day, clean_month, clean_year, clean_state, clean_city, clean_addr, clean_killed, clean_injured, clean_ms):

    # Define database pathway and establish SQL connection
    # Add echo = True after the sql path argument to see a print out of the SQL being executed

    path = db_pathway
    engine = sqlalchemy.create_engine(f'sqlite:///{path}')
    
    # Establish connection to table 
    metadata = MetaData()
    gun_violence = Table('gun_violence', metadata, autoload = True, autoload_with = engine)
    metadata.create_all(engine)
    
    # Checks each row of the table pulled from website
    # If the row already exists in the database, no change
    # If the row does not already exist in the database, it is inserted
    # This successfully avoids adding duplicate rows


    with engine.connect() as conn:
        query = f"""SELECT *
        FROM gun_violence
        WHERE date = '{clean_date}' 
        AND (state = '{clean_state}' 
        AND city = '{clean_city}'
        AND address = '{clean_addr}');"""

        df = pd.read_sql(query, conn)

        if df.empty:

            add_row(metadata, gun_violence, engine, clean_entrynum, clean_date, clean_day, clean_month, clean_year, clean_state, clean_city, clean_addr, clean_killed, clean_injured, clean_ms)
        
        else:

            for i in range(len(df)):
                if df['killed'][i] != clean_killed or df['injured'][i] != clean_injured:
                    delete_duplicate(db_path, clean_date, clean_state, clean_city, clean_addr, clean_killed, clean_injured)
                    add_row(metadata, gun_violence, engine, clean_entrynum, clean_date, clean_day, clean_month, clean_year, clean_state, clean_city, clean_addr, clean_killed, clean_injured, clean_ms)

                    
                    
new_data_pull = grab_new_data(db_path)
import_data(new_data_pull)
print("Done")
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Query can be run to ensure that duplicates do not exist in database

with engine.connect() as conn:
    query1 = """SELECT * FROM gun_violence;"""
    df1 = pd.read_sql(query1, conn)


with engine.connect() as conn:
    query1 = """SELECT * FROM gun_violence 
    WHERE date = '{clean_date}' 
    AND state = '{clean_state}' 
    AND city = '{clean_city}'
    AND address = '{clean_addr}'
    AND killed = '{clean_killed}'
    AND injured = '{clean_injured}';"""
    test = pd.read_sql(query1, conn)
    
if not df1.duplicated().unique()[0]:
    print("No duplicates found. Database length: ", len(df1))
else:
    print("There are duplicates")
