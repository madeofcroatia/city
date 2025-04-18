COMPARISON_DIV_LAYOUT = {
    'margin' : {'t' : 0, 'l' : 0, 'r' : 0, 'b' : 0},
    'showlegend' : False,
    'xaxis' : {'showticklabels' : False},
    'yaxis' : {'showticklabels' : False},
    'yaxis_title' : None,
    'xaxis_title' : None
}

MAIN_FIGURE_LAYOUT = {
    'title': 'Historical ridership data',
    'dragmode': 'select',
    'margin': {'b': 0},
    'legend': {
        'yanchor': 'top',
        'y': 0.99,
        'xanchor': 'right',
        'x': 0.99
    }
}

COMPARISON_UNIT_WIDTH = 3

DEFAULT_MODES = ['bus', 'rail']
DEFAULT_RESOLUTION = 'W'
DEFAULT_AGGREGATION = 'mean'

DAYTYPE_COLORS = ['gold', 'blue']