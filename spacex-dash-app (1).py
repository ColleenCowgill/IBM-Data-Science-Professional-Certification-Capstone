# spacex_dash_app.py

import pandas as pd
import dash
from dash import html, dcc
from dash.dependencies import Input, Output
import plotly.express as px

# ---- Load data ----
spacex_df = pd.read_csv("spacex_launch_dash.csv")
spacex_df['Payload Mass (kg)'] = pd.to_numeric(spacex_df['Payload Mass (kg)'], errors='coerce')
spacex_df['class'] = pd.to_numeric(spacex_df['class'], errors='coerce').fillna(0).astype(int)

max_payload = int(spacex_df['Payload Mass (kg)'].max())
min_payload = int(spacex_df['Payload Mass (kg)'].min())

# ---- App ----
app = dash.Dash(__name__)
server = app.server

# ---- Layout ----
app.layout = html.Div([
    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}
    ),

    dcc.Dropdown(
        id='site-dropdown',
        options=([{'label': 'All Sites', 'value': 'ALL'}] +
                 [{'label': s, 'value': s} for s in sorted(spacex_df['Launch Site'].unique())]),
        value='ALL',
        clearable=False,
        style={'width': '60%', 'margin': '0 auto 16px'}
    ),

    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P('Payload range (Kg):', style={'textAlign': 'center'}),

    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', 10000: '10000'},
        value=[min_payload, max_payload],
        allowCross=False
    ),

    html.Br(),
    html.Div(dcc.Graph(id='success-payload-scatter-chart'))
])

# ---- Pie callback ----
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        df_all = spacex_df.groupby('Launch Site', as_index=False)['class'].sum()
        fig = px.pie(df_all, values='class', names='Launch Site',
                     title='Total Successful Launches by Site')
        return fig
    else:
        site_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        counts = (site_df['class']
                  .value_counts()
                  .rename(index={1: 'Success', 0: 'Failure'})
                  .reindex(['Success', 'Failure'], fill_value=0)
                  .reset_index())
        counts.columns = ['Outcome', 'Count']
        fig = px.pie(counts, values='Count', names='Outcome',
                     title=f'Success vs Failure for {entered_site}')
        return fig

# ---- Scatter callback ----
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_success_payload_scatter(selected_site, payload_range):
    low, high = payload_range
    df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]
    if selected_site != 'ALL':
        df = df[df['Launch Site'] == selected_site]
        title = f'Payload vs. Outcome for {selected_site} ({low}-{high} kg)'
    else:
        title = f'Payload vs. Outcome for All Sites ({low}-{high} kg)'

    fig = px.scatter(
        df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        hover_data=['Launch Site'],
        labels={'class': 'Success (1=Yes, 0=No)'},
        title=title
    )
    fig.update_yaxes(tickvals=[0, 1])
    return fig

# ---- Run ----
if __name__ == '__main__':
    app.run(debug=True)