from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

app = Dash(__name__)
ridership_df = (
    pd.read_csv(
        "city/data/cta-ridership-clean.csv",
        parse_dates=['date']
    )
    .sort_values('date')
    .drop('day_type', axis='columns')
)

def get_marks(df):
    dates_to_mark = df['date'].dt.year.diff()
    marks = {int(i) : str(df.loc[i, 'date'].year) for i in np.where(dates_to_mark != 0)[0]}
    return marks

app.layout = html.Div([
    html.H4('CTA Ridership'),
    dcc.Graph(id="time-series-chart"),
    dcc.RangeSlider(
        id="dateslider",
        min=0, max=ridership_df.shape[0]-1, step=1,
        value=[0, ridership_df.shape[0]-1],
        marks=get_marks(ridership_df),
        updatemode="drag"
    ),
    html.P("Select mode of transportation:"),
    dcc.Checklist(
        id="modes",
        options={
            'bus': 'bus',
            'rail': 'train'
        },
        value=[]
    ),
    html.P("Select date resolution:"),
    dcc.RadioItems(
        id="resolution",
        options={
            'D': 'daily',
            'W': 'weekly',
            'M': 'monthly'
        },
        value='W'
    ),
    html.P("Aggregation method:"),
    dcc.RadioItems(
        id="aggregation",
        options={
            'mean' : 'mean',
            'sum' : 'sum'
        },
        value='mean'
    )
    #dcc.Checklist(
    #    id="tickers",
    #    options={
    #        'AMZN': 'Amazon',
    #        'FB': 'Facebook',
    #        'NFLX': 'Netflix'
    #    },
    #    value=['AMZN']
    #)
])

@app.callback(
    Output("time-series-chart", "figure"), 
    Input("modes", "value"),
    Input('resolution', 'value'),
    Input('aggregation', 'value'),
    Input('dateslider', 'value'))
def display_time_series(modes, resolution, aggregation, dateslider):
    #df = pd.DataFrame({
    #    "date" : pd.date_range("2020-01-01", "2021-01-01", freq="D"),
    #    "AMZN" : np.random.randint(10, 20, 367),
    #    "FB" : np.random.randint(15, 20, 367),
    #    "NFLX" : np.random.randint(10, 25, 367),
    #})
    #fig = px.line(df, x='date', y=tickers)
    min_date, max_date = dateslider
    #print(min_date, max_date)
    df = ridership_df.loc[min_date:max_date,]
    if aggregation == "mean":
        df = df.set_index('date').resample(resolution).mean().reset_index()
    elif aggregation == "sum":
        df = df.set_index('date').resample(resolution).sum().reset_index()
    fig = px.line(df, x="date", y=modes)
    return fig


app.run_server(debug=True)