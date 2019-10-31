import dash
import dash_core_components as dcc
import dash_html_components as html

from flask_caching import Cache

import plotly.graph_objs as go
from dash.dependencies import Input, Output
import numpy as np

from utils import get_latest_output, read_mongo, json_pandas
from main import get_keywords
from utils_app import tweets_per_minute, create_wordcloud_raster

# direction of the csv file
# latest_csv = get_latest_output()

# df = pd.read_csv(latest_csv)

key_words = get_keywords()[:9]




# ============== FIN FUNCIONES =============== #


# Figures for different tabs #
figure_tweets_minute_prensa = dcc.Graph(id='plot-tweets-prensa')
figure_tweets_minute_chile = dcc.Graph(id='plot-tweets-chile')
figure_tweets_minute_politico = dcc.Graph(id='plot-tweets-politico')

figure_wc_prensa = dcc.Graph(id='word-cloud-prensa')
figure_wc_chile = dcc.Graph(id='word-cloud-chile')
figure_wc_politico = dcc.Graph(id='word-cloud-politico')

# CSS #
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# se crea un objeto dash #
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
CACHE_CONFIG = {
    'CACHE_TYPE': 'filesystem',
    'CACHE_DIR': 'cache-directory'
}
cache = Cache()
cache.init_app(app.server, config=CACHE_CONFIG)

N = 100

# ======== layout config ======== #

app.layout = html.Div([

    # ======== PRESENTACION PAGINA ======== #

    html.H1(children='¡Bienvenid@ al DashBoard del CeMAS!', style={'textAlign': 'center'}),
    html.H5(children='''
    En esta página usted tiene acceso a distintas visualizaciones referentes a la situación
    actual de Chile.
    ''', style={'textAlign': 'center'}),

    html.H6(children="El objetivo es  que la ciudadanía tenga un fácil acceso a lo que estan diciendo los actores "
                     "políticos, los medios de comunicación y la ciudadanía",
            style={'textAlign': 'center'}),

    # ======== TABS PRENSA, CHILE, POLITICOS ======== #

    dcc.Tabs(id='tabs-graphs', value='tab-1-prensa', children=[
        dcc.Tab(label='Prensa', id='graphs-prensa', value='tab-1-prensa', children=html.Div([
            html.H6(
                children="Los distintos medios de comunicación chilenos utilizan .  En tiempo real, se puede ver la cantidad de Tweets realizadas por la prensa:",
                style={'textAlign': 'center'}),
            html.Div(figure_tweets_minute_prensa, style={'textAlign': 'center'}),

            html.H6("En donde las palabras que más usadas en sus tweets son:",
                    style={'textAlign': 'center'}),
            html.Div(figure_wc_prensa, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'})
        ])
                ),

        dcc.Tab(label='Chile', id='graphs-chile', value='tab-2-chile', children=html.Div([
            html.H6(
                children="Los chilenos también usan Twitter.  En tiempo real, se puede ver la frecuencia en que la gente utiliza la red social para expresarse:",
                style={'textAlign': 'center'}),
            html.Div(figure_tweets_minute_chile, style={'textAlign': 'center'}),

            html.H6("Las palabras que más usan los usuarios de twitter son:",
                    style={'textAlign': 'center'}),
            html.Div(figure_wc_chile, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'}),
        ])
                ),

        dcc.Tab(label='Politicos', id='graphs-politicos', value='tab-3-politicos', children=html.Div([
            html.H6(
                children="Twitter se ha vuelto una plataforma importante para los políticos de hoy.  La frecuencia con la que publican en Twitter es:",
                style={'textAlign': 'center'}),
            html.Div(figure_tweets_minute_politico, style={'textAlign': 'center'}),

            html.H6("Las palabras que más usan los políticos para expresarse en Twitter son:",
                    style={'textAlign': 'center'}),
            html.Div(figure_wc_politico, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'}),
        ])
                ),
    ]),

    # ======== hidden signal value ======== #
    html.Div(id='signal', style={'display': 'none'}),

    # ========  time interval ======== #
    dcc.Interval(
        id='interval',
        interval=120 * 1 * 1000,  # in milliseconds
        n_intervals=0
    ),
])


# ======== CALLBACKS ======== #

# perform expensive computations in this "global store"
# these computations are cached in a globally available
# memory store which is available across processes
# and for all time.
@cache.memoize()
def global_store():
    # Read data from db and return json
    return read_mongo('dbTweets', 'tweets_chile', query_fields={"dateTweet": 1, "tweet": 1, "screenName": 1},
                      json_only=True)


@app.callback(Output('signal', 'children'), [Input('interval', 'n_intervals')])
def compute_data(n):
    # compute value and send a signal when done
    data = global_store()
    return data


# IF CALLBACK IS FOR A FIGURE --> ONE CALLBACK PER FIG IN EACH TAB #
@app.callback(
    Output('plot-tweets-prensa', 'figure'),  # the output is what to modify and which property
    [Input('signal', 'children')]  # input is the trigger and the property
)
def update_tweets_minute_prensa(data):  # no sé pq está esa 'n' ahí, pero no la saquen que si no no funciona

    tweets_minute = tweets_per_minute(json_pandas(data), key_words)
    # get the indexes of the keywords
    # kw_dict = get_kw_dict(data)
    # dictionary of dfs
    # pandas_kw_dict = {element:data.iloc[kw_dict[element]] for element in kw_dict}

    # assign the 'created_at' column to the histogram

    traces = [go.Scatter(x=tweets_minute[key].index,
                         y=tweets_minute[key]['dateTweet'].values,
                         mode='lines+markers',
                         text=key,
                         name=key)
              for key in key_words + ['All']]

    data = {
        'data': traces
    }
    return go.Figure(data)


@app.callback(
    Output('plot-tweets-chile', 'figure'),  # the output is what to modify and which property
    [Input('signal', 'children')]  # input is the trigger and the property
)
def update_tweets_minute_chile(data):  # no sé pq está esa 'n' ahí, pero no la saquen que si no no funciona

    tweets_minute = tweets_per_minute(json_pandas(data), key_words)
    # get the indexes of the keywords
    # kw_dict = get_kw_dict(data)
    # dictionary of dfs
    # pandas_kw_dict = {element:data.iloc[kw_dict[element]] for element in kw_dict}

    # assign the 'created_at' column to the histogram

    traces = [go.Scatter(x=tweets_minute[key].index,
                         y=tweets_minute[key]['dateTweet'].values,
                         mode='lines+markers',
                         text=key,
                         name=key)
              for key in key_words + ['All']]

    data = {
        'data': traces
    }
    return go.Figure(data)


@app.callback(
    Output('plot-tweets-politico', 'figure'),  # the output is what to modify and which property
    [Input('signal', 'children')]  # input is the trigger and the property
)
def update_tweets_minute_politico(data):  # no sé pq está esa 'n' ahí, pero no la saquen que si no no funciona

    tweets_minute = tweets_per_minute(json_pandas(data), key_words)
    # get the indexes of the keywords
    # kw_dict = get_kw_dict(data)
    # dictionary of dfs
    # pandas_kw_dict = {element:data.iloc[kw_dict[element]] for element in kw_dict}

    # assign the 'created_at' column to the histogram

    traces = [go.Scatter(x=tweets_minute[key].index,
                         y=tweets_minute[key]['dateTweet'].values,
                         mode='lines+markers',
                         text=key,
                         name=key)
              for key in key_words + ['All']]

    data = {
        'data': traces
    }
    return go.Figure(data)


@app.callback(
    Output('word-cloud-prensa', 'figure'),
    [Input('signal', 'children')]
)
def update_wc_prensa(data, num_limit=10000):
    df = json_pandas(data)

    return create_wordcloud_raster(df, key_words)


@app.callback(
    Output('word-cloud-chile', 'figure'),
    [Input('signal', 'children')]
)
def update_wc_chile(data, num_limit=10000):
    df = json_pandas(data)

    return create_wordcloud_raster(df, key_words)


@app.callback(
    Output('word-cloud-politico', 'figure'),
    [Input('signal', 'children')]
)
def update_wc_politico(data, num_limit=10000):
    df = json_pandas(data)

    return create_wordcloud_raster(df, key_words)


if __name__ == '__main__':
    app.run_server(debug=True)
