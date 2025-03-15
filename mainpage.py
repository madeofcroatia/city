import pandas as pd
import plotly.express as px
import os 
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from datetime import datetime

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Define the layout
app.layout = html.Div([
    dbc.Container([
        html.H1("Chicago CTA Ridership Dashboard", className="text-center my-4"),
        html.H3("Exploring Transit Patterns Before and After the Pandemic", className="text-center text-muted mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.Label("Select Transit Type:"),
                dcc.RadioItems(
                    id='transit-type',
                    options=[
                        {'label': 'Bus', 'value': 'bus'},
                        {'label': 'Train (L)', 'value': 'rail'},
                        {'label': 'All', 'value': 'total'}
                    ],
                    value='total',
                    inline=True
                )
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.Label("Date Range:"),
                dcc.DatePickerRange(
                    id='date-range',
                    min_date_allowed=datetime(2018, 1, 1),
                    max_date_allowed=datetime(2025, 3, 2),
                    start_date=datetime(2019, 1, 1),
                    end_date=datetime(2023, 12, 31)
                )
            ], width='100%', className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                dcc.Graph(id='ridership-timeline')
            ], width=12, className="mb-4")
        ]),
        
        dbc.Row([
            dbc.Col([
                html.H4("Monthly Comparison", className="text-center"),
                dcc.Graph(id='monthly-comparison')
            ], width='10%'),
            dbc.Col([
                html.H4("Weekday vs Weekend Patterns", className="text-center"),
                dcc.Graph(id='weekday-weekend')
            ], width='10%')
        ], className="mb-4"),
        
        dbc.Row([
            dbc.Col([
                html.H4("Key Insights", className="mb-3"),
                html.Div(id='insights-container', className="p-3 border rounded")
            ], width=12)
        ])
    ])
])

# Load data function
def load_data():
    # This is a placeholder - you would replace this with actual data loading
    # from the Chicago Data Portal or your local files
    
    # For demonstration, we'll create sample data
    # In reality, you would use:
    # bus_data = pd.read_csv('bus_ridership.csv')
    # train_data = pd.read_csv('train_ridership.csv')
    
    dates = pd.date_range(start='2018-01-01', end='2023-12-31', freq='D')
    print(os.getcwd())
    # Generate sample data with a pandemic effect (drop in March 2020)
    
    data = pd.read_csv("data/cta-ridership-clean.csv", parse_dates=["date"])
    
    # Add some derived columns
    data['weekday'] = data['date'].dt.dayofweek < 5
    data['month'] = data['date'].dt.month
    data['year'] = data['date'].dt.year
    data['is_pandemic'] = data['date'] >= pd.Timestamp('2020-03-15')
    
    return data

# Create callbacks for interactivity
@app.callback(
    Output('ridership-timeline', 'figure'),
    [Input('transit-type', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_timeline(transit_type, start_date, end_date):
    df = load_data()
    
    # Filter by date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Create figure based on transit type
    if transit_type == 'bus':
        fig = px.line(filtered_df, x='date', y='bus_riders', 
                      title='CTA Bus Ridership Over Time')
    elif transit_type == 'rail':
        fig = px.line(filtered_df, x='date', y='rail_riders', 
                      title='CTA Train Ridership Over Time')
    else:
        fig = px.line(filtered_df, x='date', y=['bus_riders', 'rail_riders', 'total_riders'], 
                      title='CTA Ridership Over Time')
    
    # Add pandemic marker line
    fig.add_vline(x=pd.Timestamp('2020-03-15'), line_dash="dash", line_color="red",
                 annotation_text="Pandemic Begins", annotation_position="top right")
    
    fig.update_layout(
        xaxis_title='Date',
        yaxis_title='Number of Riders',
        legend_title='Transit Type',
        hovermode='x unified'
    )
    
    return fig

@app.callback(
    Output('monthly-comparison', 'figure'),
    [Input('transit-type', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_monthly_comparison(transit_type, start_date, end_date):
    df = load_data()
    
    # Filter by date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Group by month and year
    monthly_data = filtered_df.groupby(['year', 'month']).agg({
        'bus_riders': 'sum',
        'train_riders': 'sum',
        'total_riders': 'sum'
    }).reset_index()
    
    # Create month-year string for x-axis
    monthly_data['month_year'] = monthly_data.apply(
        lambda x: f"{x['year']}-{x['month']:02d}", axis=1
    )
    
    # Select column based on transit type
    if transit_type == 'bus':
        y_column = 'bus_riders'
        title = 'Monthly Bus Ridership'
    elif transit_type == 'train':
        y_column = 'train_riders'
        title = 'Monthly Train Ridership'
    else:
        y_column = 'total_riders'
        title = 'Monthly Total Ridership'
    
    fig = px.bar(monthly_data, x='month_year', y=y_column, title=title)
    
    # Color bars differently for pre-pandemic and pandemic periods
    pre_pandemic = monthly_data[monthly_data['year'] < 2020]
    early_pandemic = monthly_data[(monthly_data['year'] == 2020) & (monthly_data['month'] >= 3)]
    recovery = monthly_data[monthly_data['year'] > 2020]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=pre_pandemic['month_year'],
        y=pre_pandemic[y_column],
        name='Pre-Pandemic',
        marker_color='blue'
    ))
    
    fig.add_trace(go.Bar(
        x=early_pandemic['month_year'],
        y=early_pandemic[y_column],
        name='Early Pandemic',
        marker_color='red'
    ))
    
    fig.add_trace(go.Bar(
        x=recovery['month_year'],
        y=recovery[y_column],
        name='Recovery Period',
        marker_color='green'
    ))
    
    fig.update_layout(
        xaxis_title='Month',
        yaxis_title='Number of Riders',
        legend_title='Period',
        title=title,
        barmode='group',
        xaxis={'tickangle': 45}
    )
    
    return fig

@app.callback(
    Output('weekday-weekend', 'figure'),
    [Input('transit-type', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_weekday_weekend(transit_type, start_date, end_date):
    df = load_data()
    
    # Filter by date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Create a period column (pre-pandemic, pandemic, recovery)
    filtered_df['period'] = 'Pre-Pandemic'
    filtered_df.loc[filtered_df['date'] >= '2020-03-15', 'period'] = 'Pandemic'
    filtered_df.loc[filtered_df['date'] >= '2021-06-01', 'period'] = 'Recovery'
    
    # Group by period and weekday
    weekday_data = filtered_df.groupby(['period', 'weekday']).agg({
        'bus_riders': 'mean',
        'train_riders': 'mean',
        'total_riders': 'mean'
    }).reset_index()
    
    # Convert boolean to string for better labels
    weekday_data['day_type'] = weekday_data['weekday'].apply(lambda x: 'Weekday' if x else 'Weekend')
    
    # Select column based on transit type
    if transit_type == 'bus':
        y_column = 'bus_riders'
        title = 'Average Bus Ridership: Weekday vs Weekend'
    elif transit_type == 'train':
        y_column = 'train_riders'
        title = 'Average Train Ridership: Weekday vs Weekend'
    else:
        y_column = 'total_riders'
        title = 'Average Total Ridership: Weekday vs Weekend'
    
    fig = px.bar(
        weekday_data, 
        x='period', 
        y=y_column, 
        color='day_type',
        barmode='group',
        title=title
    )
    
    fig.update_layout(
        xaxis_title='Period',
        yaxis_title='Average Number of Riders',
        legend_title='Day Type'
    )
    
    return fig

@app.callback(
    Output('insights-container', 'children'),
    [Input('transit-type', 'value'),
     Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_insights(transit_type, start_date, end_date):
    df = load_data()
    
    # Filter by date
    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask]
    
    # Define periods
    pre_pandemic = filtered_df[filtered_df['date'] < '2020-03-15']
    pandemic = filtered_df[(filtered_df['date'] >= '2020-03-15') & (filtered_df['date'] < '2021-06-01')]
    recovery = filtered_df[filtered_df['date'] >= '2021-06-01']
    
    # Calculate insights
    if transit_type == 'bus':
        pre_avg = pre_pandemic['bus_riders'].mean()
        pandemic_avg = pandemic['bus_riders'].mean()
        recovery_avg = recovery['bus_riders'].mean() if not recovery.empty else None
        transit_name = "Bus"
    elif transit_type == 'train':
        pre_avg = pre_pandemic['train_riders'].mean()
        pandemic_avg = pandemic['train_riders'].mean()
        recovery_avg = recovery['train_riders'].mean() if not recovery.empty else None
        transit_name = "Train"
    else:
        pre_avg = pre_pandemic['total_riders'].mean()
        pandemic_avg = pandemic['total_riders'].mean()
        recovery_avg = recovery['total_riders'].mean() if not recovery.empty else None
        transit_name = "Total"
    
    # Generate text insights
    insights = [
        html.P(f"{transit_name} ridership dropped by {(1 - pandemic_avg/pre_avg)*100:.1f}% during the pandemic."),
    ]
    
    if recovery_avg:
        recovery_percent = (recovery_avg/pre_avg)*100
        insights.append(html.P(f"Current recovery shows ridership at {recovery_percent:.1f}% of pre-pandemic levels."))
    
    weekday_impact = html.P("Weekday ridership was more severely impacted than weekend ridership, suggesting a significant shift to remote work.")
    insights.append(weekday_impact)
    
    return insights

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
