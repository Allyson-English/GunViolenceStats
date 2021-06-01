import requests
import pandas as pd
import sqlalchemy
from headers import db_path as db_path_old


# get data from existing database to copy over

engine_old = sqlalchemy.create_engine(f"sqlite:///{db_path_old}")

with engine_old.connect() as conn:
    query = f"""SELECT * FROM gun_violence;"""
    old_db = pd.read_sql(query, conn)

    print(len(old_db))

new_format = old_db.drop(columns=['index'])
new_format.to_csv("/home/pi/Desktop/newlyformatted.csv")

new = pd.read_csv("/home/pi/Desktop/newlyformatted.csv").drop(columns=['Unnamed: 0'])
new = new.reset_index().rename(columns={'index':'entry'}).set_index('entry')
new.head()

def pull_date(text):
    
    text = text.split()
    return int(text.split()[1].replace(" ","").replace(",",""))

def pull_month(text):
    
    text = text.split()
    return text.split()[0].replace(" ","").replace(",","")

def pull_year(text):
    
    text = text.split()
    return int(text.split()[-1].replace(" ","").replace(",",""))

new_format['day'] = new_format['date'].apply(lambda x: pull_date(x))
new_format['month'] = new_format['date'].apply(lambda x: pull_month(x))
new_format['year'] = new_format['date'].apply(lambda x: pull_year(x))
new_format['date'] = pd.to_datetime(new_format['date'])

new_format = new_format[['date', 'day', 'month', 'year', 'state', 'city', 'address', 'killed', 'injured']]

new_format['vic_count'] = new_format['killed']+new_format['injured']

def MS(text):

    if int(text) >= 4:
        return True
    
    return False
new_format['mass_shooting'] = new_format['vic_count'].apply(lambda x: MS(x))
new_format = new_format.drop(columns=['vic_count'])
new_format.head()
new_format = new_format.reset_index().set_index('index')
new_format.head()

      
# Define database pathway and establish SQL connection

db_path = '/home/pi/Desktop/zerodays.db'
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Creating SQL table

with engine.connect() as conn:

    try:
        conn.execute("DROP TABLE gun_violence;")
    except:
        print("The gun_violence table does not exist yet.")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS gun_violence
        ('entry' INT,
        'date' DATE,
        'day' INT,
        'month' VARCHAR (15),
        'year' INT,
        'state' VARCHAR (50),
        'city' VARCHAR (50),
        'address' VARCHAR (250),
        'killed' INT, 
        'injured' INT,
        'mass_shooting' BOOLEAN
    );
    """)
    
with engine.connect() as conn:
    new.to_sql('gun_violence', conn, if_exists='append')


# Simple query to make sure everything is running smoothly (it is!) 

with engine.connect() as conn:
    query = "SELECT * FROM gun_violence;"
    df = pd.read_sql(query, conn)
    
df.tail()

with engine.connect() as conn:
    query = f"""SELECT MAX(entry) FROM gun_violence;"""
    max = pd.read_sql(query, conn).iloc[0][0]
