import requests
import pandas as pd
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

db_path = '.../gunviolence.db'

### Update Table Function
def update_table(db_pathway, page = 0):
    
    # Change headers to make it less obvious to site that this is scraping
    headers = {'User-Agent': '...'}
    
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
            clean = str(df['address'][i])
            clean = clean.replace("'","")
            df['address'][i] = clean

        newrow_insert(db_pathway, df)
    
    
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
            AND address = '{address_temp}' 
            AND killed = '{killed_temp}' 
            AND injured = '{injured_temp}';"""

            df = pd.read_sql(query, conn)

            if df.empty == True:

                ins = gun_violence.insert().values(date = date_temp, 
                                                   state = state_temp, 
                                                   city = city_temp, 
                                                   address = address_temp, 
                                                   killed = int(killed_temp), 
                                                   injured = int(injured_temp))

                with engine.connect() as conn:
                    conn.execute(ins)

                    
                    
update_table(db_path, page = 16)
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Query can be run to ensure that duplicates do not exist in database

with engine.connect() as conn:
    query1 = """SELECT COUNT(*) FROM gun_violence;"""
    df1 = pd.read_sql(query1, conn)
    

if not df1.duplicated()[0]:
    print(df1['COUNT(*)'][0], "entries")
else:
    print("Duplicates")
