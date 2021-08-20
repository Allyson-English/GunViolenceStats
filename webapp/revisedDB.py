import requests
import pandas as pd
import sqlalchemy
from headers import db_path as db_path_old
import censusgeocode as cg


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
    return int(text[1].replace(" ","").replace(",",""))

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
new_format = new_format.reset_index().rename(columns={'index':'entry'})
new_format = new_format.set_index('entry')
new_format.head()

      
# Define database pathway and establish SQL connection

db_path = 'zerodays_new.db'
engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')

# Creating SQL table

with engine.connect() as conn:

    try:
        conn.execute("DROP TABLE gun_violence;")
        print("Dropped Table")
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
    new_format.to_sql('gun_violence', conn, if_exists='append')


# Simple query to make sure everything is running smoothly (it is!) 

with engine.connect() as conn:
    query = "SELECT * FROM gun_violence;"
    df = pd.read_sql(query, conn)
    
df.tail()

with engine.connect() as conn:
    query = f"""SELECT MAX(entry) FROM gun_violence;"""
    max = pd.read_sql(query, conn).iloc[0][0]


### Creating FIPS Mapping Table-- Reading in and Formatting Table

fips = pd.read_csv("/home/pi/Desktop/FIPSCodes.csv", index_col=0).drop(columns=['FIPS County Code'])

def clean_ids(x, desired_len):

    x = str(x)
    while len(x) < desired_len:
        x = "0"+ x
    return x
    
fips['FIPSCd'] = fips['FIPSCd'].apply(lambda x: clean_ids(x, 5))
fips['STATEFP'] = fips['STATEFP'].apply(lambda x: clean_ids(x, 2))
fips['COUNTYFP'] = fips['COUNTYFP'].apply(lambda x: clean_ids(x, 3))

result = cg.address('75 Dayton Road', city='Redding', state='CT', zipcode='06896')

county_id = result[0]['geographies']['Counties'][0]['COUNTY']

state_id = result[0]['geographies']['States'][0]['STATE']

county_id = clean_ids(county_id, 3)
state_id = clean_ids(state_id, 2)

address_fips = state_id + county_id
print(address_fips)

fips[fips.FIPSCd == address_fips].head()

fips.head()


# Creating FIPS Mapping Table table

with engine.connect() as conn:

    try:
        conn.execute("DROP TABLE fips_mapping;")
    except:
        print("The fips_mapping table does not exist yet.")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS fips_mapping
        ('INDEX' INT,
        'STATEFP' VARCHAR(2), 
        'COUNTYFP' VARCHAR(3), 
        'TRACTCE', INT,
        'AFFGEOID' VARCHAR(30), 
        'GEOID' INT, 
        'NAME' FLOAT, 
        'LSAD' VARCHAR(10),
        'ALAND' INT, 
        'AWATER' INT, 
        'FIPSCd' VARCHAR(5), 
        'County Name' VARCHAR(25), 
        'State' VARCHAR(25)
    );
    """)

with engine.connect() as conn:
    fips.to_sql('fips_mapping', conn, if_exists='append')

with engine.connect() as conn:
    query = """SELECT * FROM gun_violence LIMIT 5;"""
    df = pd.read_sql(query, conn)
    display(df.head())

# Creating State and State Acronym Table

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'American Samoa': 'AS',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'District of Columbia': 'DC',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Guam': 'GU',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Northern Mariana Islands':'MP',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Puerto Rico': 'PR',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virgin Islands': 'VI',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY'
}

states_tbl = pd.DataFrame({'STATE': [x for x in us_state_abbrev.keys()], 'ST_ACRONYM': [x for x in us_state_abbrev.values()]})
states_tbl = states_tbl.set_index('STATE')

with engine.connect() as conn:

    try:
        conn.execute("DROP TABLE states;")
    except:
        print("The states table does not exist yet.")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS states
        ('state' VARCHAR(20), 
        'st_acronym' VARCHAR(5)
    );
    """)

with engine.connect() as conn:
    states_tbl.to_sql('states', conn, if_exists='append')

with engine.connect() as conn:
    query = "SELECT * FROM states;"
    df = pd.read_sql(query, conn)