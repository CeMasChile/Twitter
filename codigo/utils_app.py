import pandas as pd
from PIL import Image
import plotly.graph_objs as go
from wordcloud import WordCloud
from main import get_keywords
import numpy as np

key_words = get_keywords()[:9]


def get_users(direction):
    '''
    devuelve un df solo con la columna de usuarios para cargar más rápido
    '''
    return pd.read_csv(direction, usecols=['screenName'])


def get_time_text(direction):
    '''
    devuelve un df solo con la columna de horas y texto para cargar más rápido
    '''
    pd.read_csv(direction, usecols=['dateTweet', 'tweet'])


def get_kw_dict(dataframe):
    '''
        devuelve un diccionario con los índices del df que contienen cada una de las palabras clave
        ojo, eso no tiene pq sumar el total, ya que puden haber tweets con ambas palabras
    '''
    return {key_words[i]: dataframe[dataframe['tweet'].str.contains(key_words[i])].index for i in range(len(key_words))}


# FUNCIONA #
def tweets_per_minute(df, key_words=None, column='dateTweet'):
    '''
    funcion que nos dice el nro de veces que aparece una determinada fecha
    en formato df, donde el index es la fecha con hora hasta el minuto y la columna es la frecuencia
    '''

    if key_words == None:
        df.loc[:, column] = pd.to_datetime(df[column], utc=True).dt.floor('min')
        frecuencia_tweets = pd.DataFrame(df['dateTweet'].value_counts()).sort_index().iloc[1:-1]
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
    return {users[i]: dataframe[dataframe['screenName'].str.contains(users[i])].index for i in range(len(users))}


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

def get_word_frequency(dataframe, wordlist):
    """
    Count how many tweets contain a given word
    :param dataframe: Pandas dataframe from the tweepy mining
    :param wordlist: array-like with the keywords

    TODO: - drop dependency on numpy?
    """
    word_freq = dict()
    for word in wordlist:
        word_freq[word] = np.where(dataframe['tweet'].str.contains(word))[0].size

    return word_freq


def create_wordcloud_raster(dataframe, wordlist,
                            wc_kwargs=dict(background_color='white', colormap='plasma', width=1200, height=800)):
    """
    Generate a wordcloud of the keywords given, wheighted by the number of
    unique tweets they appear in. Returns a go.Figure() instance.

    :param dataframe: Pandas DataFrame object. It must contain a 'tweet' column with the
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


def get_username_list(direction):
    '''
    get a list of usernames given a direction of a csv file containing the list of usernames of interest
    :param direction: direction of file with users
    :return: a list with the users
    '''
    df = pd.read_csv(direction)
    return list(df[~df['Twitter'].isna()]['Twitter'].str[1:].values)
