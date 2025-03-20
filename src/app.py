from dash import Dash, dcc, html, Input, Output, Patch, State, ctx, no_update, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from components import comparison_mode
from utils.utils import get_df
from utils.presets import COMPARISON_DIV_LAYOUT

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
ridership_df = (
    pd.read_csv(
        "data/cta-ridership-clean.csv",
        parse_dates=['date']
    )
    .sort_values('date')
)

daytype_colors = ["gold", "blue"]
fig = px.line(
    data_frame=get_df(
        ridership_df,
        ridership_df['date'].min(), ridership_df['date'].max(),
        ['bus', 'rail'], 'W', 'mean'
    ),
    x='date',
    y=['bus', 'rail'],
    markers=True
)

fig.update_layout(
    title="Historical ridership data",
    dragmode="select",
    margin={'b' : 0},
    legend=dict(
        yanchor="top",
        y=0.99,
        xanchor="right",
        x=0.99
    )
)

"""def make_comparison_div(min_date, max_date, modes, n, width=3):
    df = (
        ridership_df.loc[
            (min_date <= ridership_df['date']) & (ridership_df['date'] <= max_date),
        ].assign(weekday = lambda x: x['day_type'] == "W")
    )
    main_top = px.line(df, x='date', y=modes)
    main_top.update_layout(**COMPARISON_DIV_LAYOUT)
    #main_top.update_layout(margin=dict(b=10, t=10))
    main_top.update_traces(line={'width' : 1})

    main_bot = px.line(
                df, x='date', y=modes,
                color_discrete_sequence=daytype_colors[:len(modes)],
                facet_col="weekday"
            )
    main_bot.update_layout(**COMPARISON_DIV_LAYOUT)
    main_bot.update_layout(margin=dict(t=20, b=0))
    main_bot.update_xaxes(showticklabels=False, title=None)
    layout = dbc.Col([
        dbc.Row([
            dbc.Col(dbc.Button("X", id={"type" : "dynamic-delete", "index" : n}, size="sm"), width="auto"),
            dbc.Col(html.Div(f"{min_date} to {max_date}"), width="auto")
        ], style={'height' : '10%'}, className="mt-1 mb-1"),
        dbc.Row(dcc.Graph(
            id=f"main-top-{n}",
            figure=main_top,
            config={'staticPlot': True}
        ), style={'height' : '55%'}),
        dbc.Row(dcc.Graph(
            id=f"main-bot-{n}",
            figure=main_bot,
            config={'staticPlot': True}
        ), style={'height' : '30%'})
    ], id=f"comparison-{n}", width=width, style={"height" : "300px"}, className="border")
    return layout"""



table_header = [
    html.Thead(html.Tr([
        html.Th(""),
        html.Th("transportation modes"),
        html.Th("date resolution"),
        html.Th("aggregation method")
    ]))
]

table_body = [html.Tbody([
    html.Tr([
        html.Td("historic ridership"),
        html.Td(dcc.Checklist(
            id="modes1",
            options={
                'bus': 'bus',
                'rail': 'rail'
            },
            value=['bus', 'rail'],
            inline=True
        )),
        html.Td(dcc.RadioItems(
            id="resolution1",
            options={
                'D' : 'D',
                'W' : 'W',
                'M' : 'M'
            },
            value='W',
            inline=True
        )),
        html.Td(dcc.RadioItems(
            id="aggregation1",
            options={
                'mean' : 'mean',
                'sum' : 'sum'
            },
            value='mean',
            inline=True
        ))
    ]),
    html.Tr([
        html.Td(dbc.Row([
            dbc.Col(html.Div(""), width="auto"),
            dbc.Col(dcc.Checklist(
                id="synchronize",
                options={'same' : 'same as historical data'},
                value=['same'],
                inline=True
            ), width="auto")
    ])),
        html.Td(dcc.Checklist(
            id="modes2",
            options=[
                {'label' : 'bus', 'value' : 'bus'},
                {'label' : 'rail', 'value' : 'rail'}
            ],
            value=['bus', 'rail'],
            inline=True
        )),
        html.Td(dcc.RadioItems(
            id="resolution2",
            options=[
                {'label' : 'D', 'value' : 'D'},
                {'label' : 'W', 'value' : 'W'},
                {'label' : 'M', 'value' : 'M'}
            ],
            value='W',
            inline=True
        )),
        html.Td(dcc.RadioItems(
            id="aggregation2",
            options=[
                {'label' : 'mean', 'value' : 'mean'},
                {'label' : 'sum', 'value' : 'sum'}
            ],
            value='mean',
            inline=True
        ))
    ], id="select-row", style={'display' : 'none'})
])]

input_table = dbc.Table(table_header + table_body, bordered=True)

app.layout = dbc.Container([
    #input_table,
    dbc.Col([
        html.H4('CTA Ridership', className="text-center"),
        dbc.Row(dcc.Graph(id="time-series-chart", figure=fig))
    ], align='center', className="mb-0"),
    dbc.Row([
        dbc.Col([
            input_table,
            dbc.Row([
                dbc.Col(dcc.Graph(id="daytype-vis")),
                #dbc.Col(dcc.Graph(id="weekdays-visualization"), width=6),
                #dbc.Col(dcc.Graph(id="weekends-visualization"), width=6)
            ], className="d-none", id="daytype-div")], width=6),
        dbc.Col([
            dbc.Row([
                dbc.Col(html.Div("Ridership from "), width="auto"),
                dbc.Col(dcc.DatePickerSingle(id="from-date"), width="auto"),
                dbc.Col(html.Div(" until "), width="auto"),
                dbc.Col(dcc.DatePickerSingle(id="till-date"), width="auto"),
                dbc.Col(dbc.Button(
                    "save timeframe", id="save-button"
                ))
            ], align="center", className="g-2 mt-0"),
            dcc.Graph(
                id='zoomed-time-series-chart'
            )],
            id="zoomed-div",
            className="d-none mt-0 mb-0",
            width=6
        )
    ], className="mb-0"),
    comparison_mode.make_comparison_div()
], fluid=True)

@app.callback(
    Output("time-series-chart", "figure"), 
    Input("modes1", "value"),
    Input('resolution1', 'value'),
    Input('aggregation1', 'value')
    )
def display_time_series(modes, resolution, aggregation):
    #print(len(old['data']), old['data'][0].keys(), old['data'][0]['line'])
    #df = pd.DataFrame({
    #    "date" : pd.date_range("2020-01-01", "2021-01-01", freq="D"),
    #    "AMZN" : np.random.randint(10, 20, 367),
    #    "FB" : np.random.randint(15, 20, 367),
    #    "NFLX" : np.random.randint(10, 25, 367),
    #})
    #fig = px.line(df, x='date', y=tickers)
    min_date, max_date = "2001-01-01", "2024-12-31"
    #print(min_date, max_date)
    df = get_df(ridership_df, min_date, max_date, modes=modes, resolution=resolution, aggregation_method=aggregation)
    fig = Patch()
    fig['data'] = [{'x' : df['date'], 'y' : df[mode], 'name' : mode} for mode in modes]
    #for i in range(2 - len(modes)):
    #    fig['data']
    #fig.update_layout(
    #    dragmode="select",
    #    selectionrevision="constant"
    #)
    return fig

@app.callback(
    Output("zoomed-time-series-chart", "figure"),
    Output("zoomed-div", "className"),
    Input("time-series-chart", "selectedData"),
    Input('modes2', 'value'),
    Input('resolution2', 'value'),
    Input('aggregation2', 'value'),
    Input('from-date', 'date'),
    Input('till-date', 'date')
)
def display_zoomed_time_series(selectedData, modes, resolution, aggregation, min_date, max_date):
    #print(selectedData)
    if selectedData is None:
        return px.line(), "d-none",
    
    if ctx.triggered_id == "time-series-chart":
        x_min, x_max = selectedData['range']['x']
        min_date = x_min.split()[0]
        max_date = x_max.split()[0]

    zoomed_df = get_df(
        ridership_df,
        min_date=min_date, max_date=max_date,
        modes=modes, resolution=resolution, aggregation_method=aggregation
    )
    fig = px.line(zoomed_df, x="date", y=modes)
    fig.update_layout(
        margin={'t' : 5, 'b' : 0},
        showlegend=False,
        xaxis=dict(
            title='Date',
            rangeslider=dict(visible=True),
            type='date'
        )
    )
    return fig, ""

@app.callback(
    Output("from-date", "date"),
    Output("till-date", "date"),
    Input("time-series-chart", "selectedData"),
)
def set_datepicker(sel_box):
    if sel_box is None:
        return None, None
    
    min_date = sel_box['range']['x'][0].split()[0]
    max_date = sel_box['range']['x'][1].split()[0]
    
    return min_date, max_date


@app.callback(
    Output("select-row", "style"),
    Input("time-series-chart", "selectedData")
)
def show_table(selection):
    #print(selection)
    if selection is None:
        return {'display' : 'none'}
    
    return {'display' : 'table-row'}

@app.callback(
    Output("modes2", "options"),
    Output("resolution2", "options"),
    Output("aggregation2", "options"),
    Output("modes2", "value"),
    Output("resolution2", "value"),
    Output("aggregation2", "value"),
    Input("synchronize", "value"),
    Input("modes1", "value"),
    Input("resolution1", "value"),
    Input("aggregation1", "value"),
    State("modes2", "options"),
    State("resolution2", "options"),
    State("aggregation2", "options")
)
def allow_select_customization(synchronization, modes1, resolution1, aggregation1, modes_opt, resolution_opt, aggregation_opt):
    #print(synchronization, modes1, resolution1, aggregation1, modes_opt)
    #print([{**opt, 'disabled' : True}
    #        for opt in modes_opt])
    if synchronization == ["same"]:
        #print(modes_opt)
        disabled_modes = [{**opt, 'disabled' : True} for opt in modes_opt]
        disabled_resolution = [{**opt, 'disabled' : True} for opt in resolution_opt]
        disabled_aggregation = [{**opt, 'disabled' : True} for opt in aggregation_opt]
        #print(disabled_aggregation)
        return disabled_modes, disabled_resolution, disabled_aggregation, modes1, resolution1, aggregation1
    
    enabled_modes = [{**opt, 'disabled' : False} for opt in modes_opt]
    enabled_resolution = [{**opt, 'disabled' : False} for opt in resolution_opt]
    enabled_aggregation = [{**opt, 'disabled' : False} for opt in aggregation_opt]

    return enabled_modes, enabled_resolution, enabled_aggregation, no_update, no_update, no_update

@app.callback(
    Output("daytype-vis", "figure"),
    Output("daytype-div", "className"),
    Input("from-date", "date"),
    Input("till-date", "date"),
    Input("modes2", "value")
)
def update_daytype_visualizations(min_date, max_date, modes):
    if min_date is None or max_date is None:
        return no_update
    
    df = (
        ridership_df.loc[
            (min_date <= ridership_df['date']) & (ridership_df['date'] <= max_date),
        ].assign(weekday = lambda x: x['day_type'] == "W")
    )

    print(df.columns)
    daytype_fig = px.line(
        df, x='date', y=modes,
        facet_col='weekday',
        color_discrete_sequence=daytype_colors[:len(modes)]
    )

    return daytype_fig, "mt-0"




@app.callback(
    Output("comparison-div", "children"),
    Input("save-button", "n_clicks"),
    State("from-date", "date"),
    State("till-date", "date"),
    State("modes2", "value"),
    Input({"type" : "dynamic-delete", "index" : ALL}, "n_clicks"),
    State("comparison-div", "children")
)
def f(n, min_date, max_date, modes, _, children):
    if max_date is None or min_date is None:
        return []
    
    print(ctx.triggered_id)

    if ctx.triggered_id == "save-button":
        patched_children = Patch()
        patched_children.append(
            comparison_mode.make_comparison_unit(ridership_df, min_date, max_date, modes, n)
        )
        return patched_children

    if ctx.triggered_id['type'] == 'dynamic-delete':
        new_children = []
        for child in children:
            if child['props']['id'] != f"comparison-{ctx.triggered_id['index']}":
                new_children.append(child)

        return new_children

    
    

    
app.run_server(debug=True)