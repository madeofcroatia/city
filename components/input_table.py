from dash import html, dcc
import dash_bootstrap_components as dbc

def make_table_header():
    table_header = [
        html.Thead(html.Tr([
            html.Th(""),
            html.Th("transportation modes"),
            html.Th("date resolution"),
            html.Th("aggregation method")
        ]))
    ]
    return table_header

def make_table_body():
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
    return table_body


def make_input_table():
    table_header = make_table_header()
    table_body = make_table_body()
    input_table = dbc.Table(table_header + table_body, bordered=True)
    return input_table
