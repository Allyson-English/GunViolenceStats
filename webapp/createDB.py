import requests
import pandas as pd
import sqlalchemy

# Read file into path

filepath = '.../gunviolence_2013_present.csv'

# Read data from csv

historical = pd.read_csv(filepath)

# Set index to incident date to match how tables are read off of HTML
# drop columsn that are not in HTML scrapped tables

historical.drop(columns = ['Incident ID', 'Operations'], inplace = True)

historical.rename(columns={'State': 'state', 
                                        'City Or County': 'city',
                                        'Address': 'address',
                                        '# Killed': 'killed',
                                        '# Injured': 'injured',
                                       'Incident Date': 'date'}, inplace = True)
        
# Define database pathway and establish SQL connection

db_path = '...gunviolence.db'
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Creating SQL table

with engine.connect() as conn:

    try:
        conn.execute("DROP TABLE gun_violence;")
    except:
        print("The gun_violence table does not exist yet.")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS gun_violence
        ('index' VARCHAR (100),
        'date' VARCHAR (100),
        'state' VARCHAR (100),
        'city' VARCHAR (100),
        'address' VARCHAR (250),
        'killed' INT, 
        'injured' INT
    );
    """)
    
with engine.connect() as conn:
    historical.to_sql('gun_violence', conn, if_exists='append')
    
# Simple query to make sure everything is running smoothly (it is!) 

with engine.connect() as conn:
    query = "SELECT * FROM gun_violence LIMIT 3;"
    df = pd.read_sql(query, conn)
    
df
