import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
import io
from wordcloud import WordCloud
from PIL import Image
import plotly.graph_objs as go
from dash.dependencies import Input, Output


from utils import get_latest_output, read_mongo
from main import get_keywords

# direction of the csv file
latest_csv = get_latest_output()

# df = pd.read_csv(latest_csv)


key_words = get_keywords()


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


def tweets_per_minute(df, column='created_at'):
    '''
    funcion que nos dice el nro de veces que aparece una determinada fecha
    en formato df, donde el index es la fecha con hora hasta el minuto y la columna es la frecuencia
    '''
    df[column] = pd.to_datetime(df[column], utc=True).dt.floor('min')
    DF = pd.DataFrame(df['created_at'].value_counts()).sort_index()
    return DF.iloc[1:-1]


def get_users_dict(dataframe, users):
    '''
    devuelve un diccionario con los índices del df que contienen cada usuario, se dan en una lista
    '''
    return {users[i]: dataframe[dataframe['user.screen_name'].str.contains(users[i])].index for i in range(len(users))}

# =========================================== FIN FUNCIONES NUEVAS=================================





def key_word_filter(df, kw, kwdict):
    """
    filtra el dataframe entregado con la palabra clave pedida usando el diccionario
    :param df: pandas dataframe to filter
    :param kw: keyword to look for
    :param kwdict: dictionary with the index values for the words
    :return: a pd dataframe with the filteres request
    """
    return df.iloc[kwdict[kw]]






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

def create_wordcloud_raster(dataframe, wordlist,
                            wc_kwargs=dict(background_color='white', colormap='plasma', width= 1200, height=800)):
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
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )
    
    return fig
 


# ============== FIN FUNCIONES =============== #


# ACÁ SE VAN A CONSTRUIR LAS PARTES DE LA APP, EN ESPECÍFICO, DE LA PARTE DE PALABRAS #

# dropdown menu
options_dropdown = [{'label': 'TODO', 'value': 'All'}] + \
                   [{'label': key_words[i].upper(), 'value': key_words[i]} for i in range(len(key_words[:9]))]

dropdown_menu = dcc.Dropdown(
    id='dropdown',
    options=options_dropdown,
    value='All',
    multi=True,
    placeholder="Seleccione las palabras clave"
)

#  time inteval
time_interval = dcc.Interval(
    id='interval',
    interval=30 * 1 * 1000,  # in milliseconds
    n_intervals=0
)

# figure
figure = dcc.Graph(id='plot')

# ACÁ TERMINA #


texto_explicativo = "En esta página usted tiene acceso a distintas herramientas para filtrar los datos que desde el " \
                    "CeMAS dejamos a su disposición. "

# css
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# se crea un objeto dash
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# layout config
app.layout = html.Div([
    html.H1('¡Bienvenid@ al DashBoard del CeMAS!'),
    html.Div(texto_explicativo),
    dropdown_menu,
    figure,
    time_interval
])


@app.callback(
    Output('plot', 'figure'),  # the output is what to modify and which property
    [Input('interval', 'n_intervals')]  # input is the trigger and the property
)
def update_graph(n):  # no sé pq está esa 'n' ahí, pero no la saquen que si no no funciona
    # Read data from db
    data = read_mongo('dbTweets', 'tweets_chile')
    tweets_minute = tweets_per_minute(data)

    # assign the 'created_at' column to the histogram
    data = {
        'data': [go.Scatter(
            x=tweets_minute.index,  # se salta el primer elemento porque no es el minuto completo
            y=tweets_minute['created_at'].values,
            mode='lines+markers'
        )]
    }

    return go.Figure(data)  # returns the figure to be updated


if __name__ == '__main__':
    app.run_server(debug=True)
