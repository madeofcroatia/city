import dash_bootstrap_components as dbc
from dash import dcc, html
from utils.presets import COMPARISON_DIV_LAYOUT, DAYTYPE_COLORS, COMPARISON_UNIT_WIDTH
import plotly.express as px

def make_comparison_div():
    return dbc.Col(
        [
            html.Hr(),
            html.H4('Comparison of timeframes', className="text-center"),
            dbc.Row(id="comparison-div", children=[], class_name="flex-nowrap overflow-auto")
        ],
        id="comparison-div-parent"
    )

def make_comparison_unit(ridership_df, min_date, max_date, modes, n):
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
                color_discrete_sequence=DAYTYPE_COLORS[:len(modes)],
                facet_col="weekday"
            )
    main_bot.update_layout(**COMPARISON_DIV_LAYOUT)
    main_bot.update_layout(margin=dict(t=20, b=0))
    main_bot.update_xaxes(showticklabels=False, title=None)
    layout = dbc.Col([
        dbc.Row([
            dbc.Col(dbc.Button("X", id={"type" : "dynamic-delete", "index" : n}, size="sm"), width="auto"),
            dbc.Col(html.Div(f"{min_date} to {max_date}"), width="auto")
        ], className="mt-1 mb-1", style={'height' : 'comparison-unit-button'}),
        dbc.Row(dcc.Graph(
            figure=main_top,
            config={'staticPlot': True}
        ), className="comparison-unit-top"),
        dbc.Row(dcc.Graph(
            figure=main_bot,
            config={'staticPlot': True}
        ), className="comparison-unit-bot")
    ], id=f"comparison-{n}", width=COMPARISON_UNIT_WIDTH, className="border comparison-unit")
    return layout