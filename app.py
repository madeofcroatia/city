from dash import Dash, dcc, html, Input, Output, Patch, State, ctx, no_update, ALL
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from components import comparison_mode
from components.input_table import make_input_table
from utils.utils import get_df
from utils.presets import DEFAULT_MODES, DEFAULT_AGGREGATION, DAYTYPE_COLORS,\
                          DEFAULT_RESOLUTION, MAIN_FIGURE_LAYOUT

app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
ridership_df = (
    pd.read_csv(
        "data/cta-ridership-clean.csv",
        parse_dates=['date']
    )
    .sort_values('date')
)

fig = px.line(
    data_frame=get_df(
        ridership_df,
        ridership_df['date'].min(), ridership_df['date'].max(),
        DEFAULT_MODES, DEFAULT_RESOLUTION, DEFAULT_AGGREGATION
    ),
    x='date',
    y=DEFAULT_MODES,
    markers=True
)

fig.update_layout(**MAIN_FIGURE_LAYOUT)

input_table = make_input_table()
comparison_div = comparison_mode.make_comparison_div()

app.layout = dbc.Container([
    dbc.Col([
        html.H4('CTA Ridership', className="text-center"),
        dbc.Row(dcc.Graph(id="time-series-chart", figure=fig))
    ], align='center', className="mb-0"),
    dbc.Row([
        dbc.Col([
            input_table,
            dbc.Row([
                dbc.Col(dcc.Graph(id="daytype-vis"))
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
    dcc.Store(id='dates'),
    dcc.Store(id='old_check'),
    comparison_div
], fluid=True)

@app.callback(
    Output("time-series-chart", "figure"), 
    Input("modes1", "value"),
    Input('resolution1', 'value'),
    Input('aggregation1', 'value')
    )
def display_time_series(modes, resolution, aggregation):
    min_date, max_date = "2001-01-01", "2024-12-31"
    df = get_df(ridership_df, min_date, max_date, modes=modes, resolution=resolution, aggregation_method=aggregation)
    fig = Patch()
    fig['data'] = [{'x' : df['date'], 'y' : df[mode], 'name' : mode} for mode in modes]
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

    #print(df.columns)
    daytype_fig = px.line(
        df, x='date', y=modes,
        facet_col='weekday',
        color_discrete_sequence=DAYTYPE_COLORS[:len(modes)]
    )

    return daytype_fig, "mt-0"




@app.callback(
    Output("dates", "data"),
    Output("comparison-div", "children"),
    Input("save-button", "n_clicks"),
    State("from-date", "date"),
    State("till-date", "date"),
    State("modes2", "value"),
    Input({"type" : "dynamic-delete", "index" : ALL}, "n_clicks"),
    State("comparison-div", "children"),
    State("dates", "data")
)
def f(n, min_date, max_date, modes, _, children, dates):
    if max_date is None or min_date is None:
        return None, []
    if dates is None:
        dates = []
    new_dates = []
    
    if ctx.triggered_id == "save-button":
        patched_children = Patch()
        patched_children.append(
            comparison_mode.make_comparison_unit(ridership_df, min_date, max_date, modes, n)
        )
        new_dates = dates + [{'min_date' : min_date, 'max_date' : max_date}]
        return new_dates, patched_children

    if ctx.triggered_id['type'] == 'dynamic-delete':
        new_children = []
        for i, child in enumerate(children):
            if child['props']['id'] != f"comparison-{ctx.triggered_id['index']}":
                new_dates.append(dates[i])
                new_children.append(child)

        return new_dates, new_children


@app.callback(
    Output('old_check', 'data'),
    Output('close-comparison-unit-left', 'children'),
    Output('close-comparison-unit-right', 'children'),
    Input({'type': 'comparison-unit-check', 'index': ALL}, 'value'),
    State('close-comparison-unit-left', 'children'),
    State('close-comparison-unit-right', 'children'),
    State('comparison-div', 'children'),
    State('dates', 'data'),
    State('old_check', 'data')
#    State({'type' : })
)
def update_close_comparison_graph(check, left, right, children, dates, old): 
    #print(old)
    if check == []:
        #print(f"{[1, 2, 3]}")
        return [{'old' : check}], left, right

    if len(old[0]['old']) < len(check):
        return [{'old' : check}], left, right
    triggered_index = None
    for i, child in enumerate(children):
        if child['props']['id'] == f'comparison-{ctx.triggered_id["index"]}':
            triggered_index = i
            break

    def add_graph():
        min_date = dates[triggered_index]['min_date']
        max_date = dates[triggered_index]['max_date']
        
        graph = comparison_mode.make_close_comparison_unit(ridership_df, min_date, max_date, DEFAULT_MODES, ctx.triggered_id['index'])
        if left['props']['id']['type'] == 'default-container':
            return graph, right
        elif right['props']['id']['type'] == 'default-container':
            return left, graph
        #print(1)
    

    def remove_graph():
        #print(left['props']['id']['type'])
        if left['props']['id']['type'] != 'default-container':
            print(left['props']['id']['index'], ctx.triggered_id['index'])
            if left['props']['id']['index'] == ctx.triggered_id['index']:
                return comparison_mode.default_container, right
        
        if right['props']['id']['type'] != 'default-container':
            if right['props']['id']['index'] == ctx.triggered_id['index']:
                return left, comparison_mode.default_container
        
        #print(2)
    
    #print(check, triggered_index)
    #print(ctx.triggered_id)
    if check[triggered_index] == [True]:
        left_graph, right_graph = add_graph()
        return [{'old' : check}], left_graph, right_graph
    
    old_checked = 0
    for el in old[0]['old']:
        if el == [True]:
            old_checked += 1

    new_checked = 0
    for el in check:
        if el == [True]:
            new_checked += 1
    
    if new_checked == old_checked:
        return [{'old' : check}], no_update, no_update
    
    left_graph, right_graph = remove_graph()
    return [{'old' : check}], left_graph, right_graph


@app.callback(
    Output({'type': 'comparison-unit-check', 'index': ALL}, 'options'),
    Input({'type': 'comparison-unit-check', 'index': ALL}, 'value'),
    State({'type': 'comparison-unit-check', 'index': ALL}, 'options')
)
def disable_comparison_unit_checks(check, opts):
    val = 0
    #print(opts)
    for c in check:
        if c == [True]:
            val += 1
    #print(val)

    new_options = []
    if val == 2:
        for i, opt in enumerate(opts):
            print(opt)
            if check[i] == [True]:
                new_options.append(opt)
            else:
                new_options.append([{**opt[0], 'disabled': True}])
    else:
        for opt in opts:
            print(opt)
            new_options.append([{**opt[0], 'disabled': False}])

    return new_options

    
    #if left['props']['id']['type'] == 'default-container':

        




app.run_server(debug=True)

