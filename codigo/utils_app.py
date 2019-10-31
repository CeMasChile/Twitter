import pandas as pd
import numpy as np


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

