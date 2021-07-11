from headers import db_path
from flask import Flask, render_template, request, jsonify, Markup
import pandas as pd
from datetime import datetime, timedelta
from dateutil import tz
import sqlalchemy
from sqlalchemy import Table, Column, Integer, String, MetaData

import json
import plotly
import plotly.express as px
from plotly.offline import plot

app = Flask(__name__)

@app.context_processor
def my_utility_processor():

    def plot_vis():

        DC_tz = tz.gettz("US/Eastern")
        today = datetime.now(tz=DC_tz)

        today_month = today.strftime('%B')
        today_date = int(today.strftime('%d'))
        today_year = today.strftime('%Y')

        yesterday = today - timedelta(days=1)
        yesterday_month = yesterday.strftime('%B')
        yesterday_date = int(yesterday.strftime('%d'))
        yesterday_year = yesterday.strftime('%Y')

        today = f"{today_month} {today_date}, {today_year}"
        yesterday = f"{yesterday_month} {yesterday_date}, {yesterday_year}"

        engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

        with engine.connect() as conn:
            query = f"""
            SELECT gv.date, gv.day, gv.month, gv.year, gv.state, 
            gv.killed, gv.injured, gv.killed+gv.injured as incidents, st.st_acronym FROM gun_violence gv
            JOIN states st ON gv.state = st.state
            WHERE day = '{today_date}' AND month = '{today_month}' AND year = '{today_year}' AND killed > 0 
            OR day = '{today_date}' AND month = '{today_month}' AND year = '{today_year}' AND injured > 0 
            OR day = '{yesterday_date}' AND month = '{yesterday_month}' AND year = '{yesterday_year}' AND killed > 0
            OR day = '{yesterday_date}' AND month = '{yesterday_month}' AND year = '{yesterday_year}' AND injured > 0
            GROUP BY gv.state;"""
            df = pd.read_sql(query, conn)
            df = df.drop_duplicates()


        states = df['st_acronym'].to_list()
        df['text'] = df.apply(lambda x: f"Killed: {x.killed}<br>Injured: {x.injured}<br><b><i>{x.state}</i></b>", axis=1)

        # plotly express bar chart
        fig = px.choropleth(data_frame=df,
                            locations=states, 
                            locationmode="USA-states", color=df.incidents.to_list(),
                            scope="usa",
                            template="plotly_dark",
                            hover_name=df.text.to_list()
            )
        fig.update_layout(paper_bgcolor="black", # background color of graph
            coloraxis_colorbar=dict( # heatmap colors
            title={
                'text': "Injuries and Fatalities <br><i>Combined Total</i><br> &nbsp;", # as with html, &nbsp; forces an empty space above bar to avoid crowding
                'side': 'top' #can be middle, bottom or top; this is default
            },
            ticks="outside", #heatmap label tickmarks
            yanchor= "top",     
            # thicknessmode="pixels", thickness=50,
            # lenmode="pixels", len=200, 
            y=1, 
            x=.75, #x sets how close the color bar is to graph; .5 is right in the middle of it
            dtick=1 # intervals for heatmap
        ))
        fig.update_layout(
            dragmode = False,
            title={
                'text': f'Incidents of Gun Violence in United States <br> <i>{yesterday}-{today}</i><br><br>',
                'y':.1,
                'x':0.5,
                'xanchor': 'center',
                'yanchor': 'top'
                }, 
            font=dict(
                family="Fjord One",
                size=16
                )
        )
        fig.update_traces(hovertemplate=None) #override default hover variables; customize preferences using title text option (above)


        return Markup(plot(fig,
                include_plotlyjs=False,
                output_type='div',
                config= {'scrollZoom': False, 
                'displayModeBar': False
                }
                ))

    return dict(plot_vis=plot_vis)

@app.route("/", methods=['GET'])
def index():
    
    DC_tz = tz.gettz("US/Eastern")
    today = datetime.now(tz=DC_tz)

    today_month = today.strftime('%B')
    today_date = int(today.strftime('%d'))
    today_year = today.strftime('%Y')

    yesterday = today - timedelta(days=1)
    yesterday_month = yesterday.strftime('%B')
    yesterday_date = int(yesterday.strftime('%d'))
    yesterday_year = yesterday.strftime('%Y')

    today = f"{today_month} {today_date}, {today_year}"
    yesterday = f"{yesterday_month} {yesterday_date}, {yesterday_year}"

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")

    with engine.connect() as conn:
        query = f"""SELECT * FROM gun_violence
        WHERE day = '{today_date}' AND month = '{today_month}' AND year = '{today_year}' AND killed > 0 
        OR day = '{today_date}' AND month = '{today_month}' AND year = '{today_year}' AND injured > 0 
        OR day = '{yesterday_date}' AND month = '{yesterday_month}' AND year = '{yesterday_year}' AND killed > 0
        OR day = '{yesterday_date}' AND month = '{yesterday_month}' AND year = '{yesterday_year}' AND injured > 0
        GROUP BY state;"""
        df = pd.read_sql(query, conn)
        df = df.drop_duplicates()

    states_count = len(df)
    states_names = df["state"].unique()
    deaths = df["killed"].sum()
    injuries = df["injured"].sum()

    twitter_statement = f"https://www.twitter.com/intent/tweet?url=In the past 24 hours, across {states_count} US states, there have been {deaths} deaths and {injuries} injuries attributed to gun violence. Track daily incidence of gun violence @ZeroDaysLive."
    
    return render_template("index.html", df=df, states_count=states_count, states_names=states_names,
                           today=today, deaths=deaths, injuries=injuries, twitter_statement=twitter_statement)



@app.route("/<state>")
def state_stats(state):

    engine = sqlalchemy.create_engine(f"sqlite:///{db_path}")


    with engine.connect() as conn:
        query1 = f"""SELECT * FROM gun_violence WHERE state IN
                    (SELECT state from states WHERE st_acronym = '{state}');"""
        dc_df = pd.read_sql(query1, conn)


    dc_df_len = len(dc_df)

    return render_template("state_stats.html", dc_df=dc_df, dc_df_len=dc_df_len)



if __name__ == "__main__":
    app.run(debug=True)
