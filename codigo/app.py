import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import numpy as np


def getDf2plot(direction):
    df = pd.read_csv(direction)
    DF = pd.to_datetime(df['created_at']).dt.floor('min')
    max_date = DF.max()
    DF = pd.to_datetime(DF.loc[DF < max_date])
    DF = DF.sort_index().value_counts()
    data = {'date': DF.index, 'freq': DF.values}
    data = pd.DataFrame(data).sort_values('date')
    return data



# direction of the css file
direction = './OutputStreaming_20191026-225744.csv'

# css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# se crea un objeto dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# layout config
app.layout = html.Div([
    # figure object
    dcc.Graph(id='hist'),
    # interval in milliseconds to update the figure
    dcc.Interval(
        id='interval',
        interval=20 * 1 * 1000,  # in milliseconds
        n_intervals=0
    )
])



@app.callback(
    Output('hist', 'figure'),           # the output is what to modify and which property
    [Input('interval', 'n_intervals')]  # input is the trigger and the property
)
# how to update the figure
def update_graph(n):
    # update a pandas DataFrame

    data = getDf2plot(direction)

    # assign the 'created_at' column to the histogram
    data = {
        'data': [go.Scatter(
            x=data['date'][1:],     # se salta el primer elemento porque no es el minuto completo
            y=data['freq'][1:],
            mode='lines+markers'
        )]
    }

    return go.Figure(data)  # returns the figure to be updated

if __name__ == '__main__':
    app.run_server(debug=True)
