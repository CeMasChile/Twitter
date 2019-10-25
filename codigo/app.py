import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go



external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

df = pd.read_csv(direction)

available_indicators = df['created_at'].unique()

app.layout = html.Div([
    dcc.Graph(id='hist'),
    dcc.Interval(
        id='interval',
        interval=1 * 1000,  # in milliseconds
        n_intervals=0
    )
])



@app.callback(
    Output('hist', 'figure'),
    [Input('interval', 'n_intervals')]
)
def update_graph(n):
    df.update(pd.read_csv(direction))


    return {
        'data': [go.Histogram(
            x=df['created_at']
        )]
    }

if __name__ == '__main__':
    app.run_server(debug=True)




