import pandas as pd
import censusgeocode as cg
import sqlalchemy
from headers import db_path


engine = sqlalchemy.create_engine(f'sqlite:///{db_path}')


with engine.connect() as conn:
    query = """SELECT * FROM fips_mapping LIMIT 5;"""
    df = pd.read_sql(query, conn)
    display(df.head())

with engine.connect() as conn:
    query = """SELECT * FROM gun_violence LIMIT 5;"""
    df = pd.read_sql(query, conn)
    display(df.head())

df['FIPS'] = ''

def clean_ids(x, desired_len):

    x = str(x)
    while len(x) < desired_len:
        x = "0"+ x
    return x
    

for i in range(len(df)):
    address = df.iloc[i]['address']
    state = df.iloc[i]['state']
    city = df.iloc[i]['city']

    result = cg.address(address, city=city, state=state)

    county_id = result[0]['geographies']['Counties'][0]['COUNTY']
    state_id = result[0]['geographies']['States'][0]['STATE']

    county_id = clean_ids(county_id, 3)
    state_id = clean_ids(state_id, 2)

    address_fips = state_id + county_id
    df.iloc[i]['FIPS'] = address_fips



import plotly
import plotly.express as px
from plotly.offline import plot

fig = px.choropleth(locations=["California", "TX", "NY"], locationmode="USA-states", color=[1,2,3], scope="usa")
fig.show()

# data
df = px.data.gapminder().query("continent=='Oceania'")

# plotly express bar chart
fig = px.line(df, x="year", y="lifeExp", color='country')

# html file
plotly.offline.plot(fig, filename='lifeExp.html')

plot(fig,
     include_plotlyjs=False,
     output_type='div')

