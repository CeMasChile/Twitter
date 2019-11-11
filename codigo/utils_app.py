import numpy as np
import pandas as pd
import plotly.graph_objs as go
from PIL import Image
from wordcloud import WordCloud


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


def get_kw_dict(df, keywords, col='tweet'):
    '''
        devuelve un diccionario con los índices del df que contienen cada una de las palabras clave
        ojo, eso no tiene pq sumar el total, ya que puden haber tweets con ambas palabras
    '''
    return {kw: df[df[col].str.contains(kw)].index for kw in keywords}


def get_tpm(df, keywords=None, column='dateTweet', wholedf=None):
    '''
    funcion que nos dice el nro de veces que aparece una determinada fecha
    en formato df, donde el index es la fecha con hora hasta el minuto y la columna es la frecuencia
    '''
    if wholedf is None:
        wholedf = df

    wholedf.loc[:, column] = pd.to_datetime(wholedf[column], utc=True).dt.floor('min')
    index_frecuencia_tweets = \
        pd.DataFrame(wholedf[column].value_counts()).sort_index().iloc[1:-1].index

    if (keywords is None):
        df.loc[:, column] = pd.to_datetime(df[column], utc=True).dt.floor('min')
        frecuencia_tweets = pd.DataFrame(df[column].value_counts()).sort_index().iloc[1:-1]
        return frecuencia_tweets.reindex(index_frecuencia_tweets).fillna(0)
    else:
        pandas_dict = get_pandas_dict(df, keywords)
        DTime = {key: get_tpm(pandas_dict[key]) for key in pandas_dict}
        DTime = {key: DTime[key].reindex(index_frecuencia_tweets).fillna(0) for key in DTime}
        return DTime


def get_users_indices(df, users, col='screenName'):
    '''
    crea una lista con los indices correspondientes a cada todos los usuarios solicitados
    :param df: dataframe de la db
    :param users: lista de usuarios para buscar
    :return: devuelve una lista con las caracteristicas descritas
    '''
    return df[df[col].isin(users)].index


def get_tpm_users(df, users, keywords):
    '''
    function that gets a df and the indices of interest to filter users
    :param df: dataframe from db
    :param users: lista de usuarios para buscar
    :param key_words: keywords to look for
    :return: return a dataframe with the words frequency but for username filter
    '''
    # return get_tpm(df.loc[df['screenName'].isin(users)], keywords)
    indices = get_users_indices(df, users)
    index_time = pd.to_datetime(pd.Index(df['dateTweet'].sort_values().unique()), utc=True)
    politicosdf = df.iloc[indices].filter(['tweet', 'dateTweet'])
    politicosdf['All'] = 1

    for word in keywords:
        politicosdf[word] = politicosdf['tweet'].str.contains(word).astype(int)
    politicosdf = politicosdf.loc[:, politicosdf.columns != 'tweet']
    politicosdf = politicosdf.groupby('dateTweet').sum()

    return politicosdf.reindex(index_time).fillna(0)


def get_pandas_dict(df, keywords):
    '''
    crea un diccionariocon los indices correspondientes a cadapalabra clave, la palabra clave es la key
    :param df: dataframe de la db
    :param keywords: keywords para buscar
    :return: devuelve un diccionario con las caracteristicas descritas
    '''
    kwdic = get_kw_dict(df, keywords)
    DD = {key: df.ix[kwdic[key]] for key in keywords}
    DD['All'] = df
    return DD


def get_word_frequency(tpm, keywords):
    """
    Count how many tweets contain a given word
    :param tpm: Dataframe with the words frequency per minute.
    :param wordlist: array-like with the keywords

    TODO: - drop dependency on numpy?
    """
    return {key: np.sum(tpm[key]['dateTweet'].values) for key in keywords}


def create_graph(tpm, keywords):
    traces = [go.Scatter(x=tpm[key].index, y=tpm[key]['dateTweet'].values,
                         mode='lines+markers', text=key, name=key)
              for key in keywords]

    graph = go.Figure({'data': traces})

    return graph


def create_wc(tpm: object, keywords: object, wc_kwargs: object = {"background_color": 'white', "colormap": 'plasma',
                                                                  "width": 700, "height": 900}) -> object:
    """
    Generate a wordcloud of the keywords given, wheighted by the number of
    unique tweets they appear in. Returns a go.Figure() instance.

    :param tpm: Dataframe with the words frequency per minute.
    :param keywords: list of strings to plot in the word cloud.
    :param wc_kwargs: dict of keyword arguments to give to the WordCloud
    constructor.
    """
    # Build the word cloud from the data
    wf = get_word_frequency(tpm, keywords)
    new_keywords = []
    for key in keywords:
        if wf[key] > 0:
            new_keywords.append(key)

    keywords = new_keywords
    wf = {key: wf[key] for key in keywords}
    if len(wf) == 0:
        return go.Figure()
    else:
        word_cloud = WordCloud(**wc_kwargs).generate_from_frequencies(wf)

        wc_raster = Image.fromarray(word_cloud.to_array())

        # Call the constructor of Figure object
        fig = go.Figure()

        # Constants
        img_width = 700
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


def create_wc2(counter: object, n: object = 35, wc_kwargs: object = {"background_color": 'white', "colormap": 'plasma',
                                                                     "width": 700, "height": 900}) -> object:
    """
    Generate a wordcloud of the keywords given, wheighted by the number of
    unique tweets they appear in. Returns a go.Figure() instance.

    :param counter: Counter with the processed words
    :param n: Number of most common words to display
    :param wc_kwargs: dict of keyword arguments to give to the WordCloud
    constructor.
    TODO: test corner cases
    """
    # Build the word cloud from the data
    # wf = get_word_frequency(tpm, keywords)
    # new_keywords = []
    # for key in keywords:
    #    if wf[key] > 0:
    #        new_keywords.append(key)

    # keywords = new_keywords
    # wf = {key:wf[key] for key in keywords}
    # if len(wf) == 0:
    #    return go.Figure()
    # else:
    filtered_ctr = dict(counter.most_common(n))
    word_cloud = WordCloud(**wc_kwargs).generate_from_frequencies(filtered_ctr)

    wc_raster = Image.fromarray(word_cloud.to_array())

    # Call the constructor of Figure object
    fig = go.Figure()

    # Constants
    img_width = 700
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
