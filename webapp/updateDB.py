from headers import headers, db_path
import requests
import pandas as pd
import sqlite3
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

### Update Table Function
def update_table(db_pathway, page = 10):
    
    # Scrape data from website
    
    for i in range(0, page):
        weblink = f'https://www.gunviolencearchive.org/last-72-hours?page={i}'
        page = requests.get(weblink, headers=headers)
        page = page.text
    
    
        # Use pandas read_html function to pull the current table from the website 
        df = pd.read_html(page, header=0, index_col=0)
        df = df[0].reset_index().drop(columns = ['Operations'])
        df.columns = ['date', 'state', 'city', 'address', 'killed', 'injured']

        for i in range(len(df)):
            clean_add = str(df['address'][i])
            clean_city = str(df['city'][i])
            clean_add = clean_add.replace("(","").replace(",","").replace("'","").replace(")","")
            clean_city = clean_city.replace("(","").replace(",","").replace("'","").replace(")","")
            df.loc[i, 'address'] = clean_add
            df.loc[i, 'city'] = clean_city

        newrow_insert(db_pathway, df)
    
        
### If duplicate date exists, delete 
def delete_duplicate(db_pathway, date_temp, state_temp, city_temp, address_temp):
    
    sqliteConnection = sqlite3.connect(db_pathway)

    try:
        cursor = sqliteConnection.cursor()

        del_statement = f"""DELETE FROM gun_violence WHERE date = '{date_temp}'  AND state = '{state_temp}'  AND city = '{city_temp}'  AND address = '{address_temp}';"""
        cursor.execute(del_statement)
        sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Failed to delete record from sqlite table", error)
    finally:
        if (sqliteConnection):
            sqliteConnection.close()
    
### After ensuring the row will not be a duplicate, add new row 
def add_row(metadata, gun_violence, engine, date_temp, state_temp, city_temp, address_temp, killed_temp, injured_temp):

    metadata.create_all(engine)
    
    ins = gun_violence.insert().values(date = date_temp, 
                                   state = state_temp, 
                                   city = city_temp, 
                                   address = address_temp, 
                                   killed = int(killed_temp), 
                                   injured = int(injured_temp))

    with engine.connect() as conn:
        conn.execute(ins)
    
    
### Insert Rows SQL Function
def newrow_insert(db_pathway, data):

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

    for row in range(len(data)):
            date_temp = data['date'][row]
            state_temp = data['state'][row]
            city_temp = data['city'][row]
            address_temp = data['address'][row]
            killed_temp = data['killed'][row]
            injured_temp = data['injured'][row]

            with engine.connect() as conn:
                query = f"""SELECT *
                FROM gun_violence
                WHERE date = '{date_temp}' 
                AND state = '{state_temp}' 
                AND city = '{city_temp}' 
                AND address = '{address_temp}';"""

                df = pd.read_sql(query, conn)

                if df.empty == True:

                    add_row(metadata, gun_violence, engine, date_temp, state_temp, city_temp, address_temp, killed_temp, injured_temp)

                elif df['killed'][0] != killed_temp or df['injured'][0] != injured_temp:

                    delete_duplicate(db_path, date_temp, state_temp, city_temp, address_temp)

                    add_row(metadata, gun_violence, engine, date_temp, state_temp, city_temp, address_temp, killed_temp, injured_temp)
                else:
                    pass

                    
                    
update_table(db_path)
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Query can be run to ensure that duplicates do not exist in database

with engine.connect() as conn:
    query1 = """SELECT * FROM gun_violence;"""
    df1 = pd.read_sql(query1, conn)
    
if not df1.duplicated().unique()[0]:
    print(len(df1))
else:
    print("There are duplicates")
