import os

import dash
from datetime import datetime, timedelta
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from flask_caching import Cache

from wordcloud import WordCloud
from PIL import Image
import plotly.graph_objs as go
from dash.dependencies import Input, Output

from utils import get_latest_output, read_mongo, json_pandas
from main import get_keywords

# direction of the csv file
# latest_csv = get_latest_output()

# df = pd.read_csv(latest_csv)

key_words = get_keywords()[:9]


# ============== FUNCIONES =============== #


# ===========================================FUNCIONES NUEVAS=================================


def get_users(direction):
    '''
    devuelve un df solo con la columna de usuarios para cargar más rápido
    '''
    return pd.read_csv(direction, usecols=['user.screen_name'])

def get_time_text(direction):
    '''
    devuelve un df solo con la columna de horas y texto para cargar más rápido
    '''
    pd.read_csv(direction, usecols=['created_at', 'text'])

def get_kw_dict(dataframe):
    '''
        devuelve un diccionario con los índices del df que contienen cada una de las palabras clave
        ojo, eso no tiene pq sumar el total, ya que puden haber tweets con ambas palabras
    '''
    return {key_words[i]: dataframe[dataframe['text'].str.contains(key_words[i])].index for i in range(len(key_words))}

# FUNCIONA #
def tweets_per_minute(df, key_words=None, column='created_at'):
    '''
    funcion que nos dice el nro de veces que aparece una determinada fecha
    en formato df, donde el index es la fecha con hora hasta el minuto y la columna es la frecuencia
    '''

    if key_words==None:
        df.loc[:, column] = pd.to_datetime(df[column], utc=True).dt.floor('min')
        frecuencia_tweets = pd.DataFrame(df['created_at'].value_counts()).sort_index().iloc[1:-1]
        return frecuencia_tweets
    else:
        pandas_dict = get_pandas_dict(df, key_words)
        DTime = {key: tweets_per_minute(pandas_dict[key]) for key in pandas_dict}
        DTime = {key: DTime[key].reindex(DTime['All'].index).fillna(0) for key in DTime}
        return DTime



def get_users_dict(dataframe, users):
    '''
    crea un diccionariocon los indices correspondientes a cada usuario, el usuario es la key
    :param df: dataframe de la db
    :param keywords: keywords para buscar
    :return: devuelve un diccionario con las caracteristicas descritas
    '''
    return {users[i]: dataframe[dataframe['user.screen_name'].str.contains(users[i])].index for i in range(len(users))}


def get_pandas_dict(df, keywords):
    '''
    crea un diccionariocon los indices correspondientes a cadapalabra clave, la palabra clave es la key
    :param df: dataframe de la db
    :param keywords: keywords para buscar
    :return: devuelve un diccionario con las caracteristicas descritas
    '''
    kwdic = get_kw_dict(df)
    DD = {word: df.iloc[kwdic[word]] for word in keywords}
    DD['All'] = df
    return DD



# =========================================== FIN FUNCIONES NUEVAS=================================


def get_word_frequency(dataframe, wordlist):
    """
    Count how many tweets contain a given word
    :param dataframe: Pandas dataframe from the tweepy mining
    :param wordlist: array-like with the keywords

    TODO: - drop dependency on numpy?
    """
    word_freq = dict()
    for word in wordlist:
        word_freq[word] = np.where(dataframe['text'].str.contains(word))[0].size

    return word_freq

# FUNCIONA #
def create_wordcloud_raster(dataframe, wordlist,
                            wc_kwargs=dict(background_color='white', colormap='plasma', width=1200, height=800)):
    """
    Generate a wordcloud of the keywords given, wheighted by the number of
    unique tweets they appear in. Returns a go.Figure() instance.

    :param dataframe: Pandas DataFrame object. It must contain a 'text' column with the
    tweets from the stream.
    :param wordlist: list of strings to plot in the word cloud.
    :param wc_kwargs: dict of keyword arguments to give to the WordCloud
    constructor.
    """

    # Build the word cloud from the data
    wf = get_word_frequency(dataframe, wordlist)
    word_cloud = WordCloud(**wc_kwargs).generate_from_frequencies(wf)

    wc_raster = Image.fromarray(word_cloud.to_array())

    # Call the constructor of Figure object
    fig = go.Figure()

    # Constants
    img_width = 1600
    img_height = 900
    scale_factor = 0.5

    # Add invisible scatter trace.
    # This trace is added to help the autoresize logic work.
    fig.add_trace(
        go.Scatter(
            x=[0, img_width * scale_factor],
            y=[0, img_height * scale_factor],
            mode="markers",
            marker_opacity=0
        )
    )

    # Configure axes
    fig.update_xaxes(
        visible=False,
        range=[0, img_width * scale_factor]
    )

    fig.update_yaxes(
        visible=False,
        range=[0, img_height * scale_factor],
        # the scaleanchor attribute ensures that the aspect ratio stays constant
        scaleanchor="x"
    )

    # Add image
    fig.update_layout(
        images=[go.layout.Image(
            x=0,
            sizex=img_width * scale_factor,
            y=img_height * scale_factor,
            sizey=img_height * scale_factor,
            xref="x",
            yref="y",
            opacity=1.0,
            layer="below",
            sizing="stretch",
            source=wc_raster)]
    )

    # Configure other layout
    fig.update_layout(
        width=img_width * scale_factor,
        height=img_height * scale_factor,
        margin={"l": 0, "r": 0, "t": 0, "b": 0}
    )

    return fig


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
            html.H6(children="Los distintos medios de comunicación chilenos utilizan .  En tiempo real, se puede ver la cantidad de Tweets realizadas por la prensa:", style={'textAlign': 'center'}),
            html.Div(figure_tweets_minute_prensa, style={'textAlign': 'center'}),

            html.H6("En donde las palabras que más usadas en sus tweets son:",
                    style={'textAlign': 'center'}),
            html.Div(figure_wc_prensa, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'})
        ])
                ),

        dcc.Tab(label='Chile', id='graphs-chile', value='tab-2-chile', children=html.Div([
            html.H6(children="Los chilenos también usan Twitter.  En tiempo real, se puede ver la frecuencia en que la gente utiliza la red social para expresarse:", style={'textAlign': 'center'}),
            html.Div(figure_tweets_minute_chile, style={'textAlign': 'center'}),

            html.H6("Las palabras que más usan los usuarios de twitter son:",
                    style={'textAlign': 'center'}),
            html.Div(figure_wc_chile, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'}),
        ])
                ),

        dcc.Tab(label='Politicos', id='graphs-politicos', value='tab-3-politicos', children=html.Div([
            html.H6(children="Twitter se ha vuelto una plataforma importante para los políticos de hoy.  La frecuencia con la que publican en Twitter es:", style={'textAlign': 'center'}),
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
    return read_mongo('dbTweets', 'tweets_chile', query_fields={"created_at": 1, "text": 1}, json_only=True)


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
                         y=tweets_minute[key]['created_at'].values,
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
                         y=tweets_minute[key]['created_at'].values,
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
                         y=tweets_minute[key]['created_at'].values,
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
    df = read_mongo('dbTweets', 'tweets_chile',
                    query_fields={"created_at": 1, "text": 1}, num_limit=num_limit)

    return create_wordcloud_raster(df, key_words)


@app.callback(
    Output('word-cloud-chile', 'figure'),
    [Input('signal', 'children')]
)
def update_wc_chile(data, num_limit=10000):
    df = read_mongo('dbTweets', 'tweets_chile',
                    query_fields={"created_at": 1, "text": 1}, num_limit=num_limit)

    return create_wordcloud_raster(df, key_words)


@app.callback(
    Output('word-cloud-politico', 'figure'),
    [Input('signal', 'children')]
)
def update_wc_politico(data, num_limit=10000):
    df = read_mongo('dbTweets', 'tweets_chile',
                    query_fields={"created_at": 1, "text": 1}, num_limit=num_limit)

    return create_wordcloud_raster(df, key_words)


if __name__ == '__main__':
    app.run_server(debug=True)
