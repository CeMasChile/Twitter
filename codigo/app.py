import warnings
import dash
import dash_core_components as dcc
import dash_html_components as html

warnings.filterwarnings('ignore')
from dash.dependencies import Input, Output
from multiprocessing import Process, Queue
from utils import read_mongo, json_pandas
from main import get_keywords
from utils_app import get_tpm, create_graph, create_wc, get_username_list, create_wc2
from npl_utils import init_counter, process

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# global variables
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
dir_noticias = 'data/Noticieros Twitter.csv'
dir_politicos = 'data/Politicos-Twitter.csv'

keywords = get_keywords()[:50]
noticieros = get_username_list(dir_noticias)
politicos = get_username_list(dir_politicos)

time_interval = 30  # seconds

# dataframe with starting database
df = json_pandas(
    read_mongo('dbTweets', 'tweets_chile',
               query_fields={"dateTweet": 1, "tweet": 1, "screenName": 1},
               json_only=True, num_limit=10 ** 5)
)

twiterator = map(process, df['tweet'])
word_counter = init_counter(twiterator)

tpm_chile = get_tpm(df.copy(), keywords)
datetime_chile = tpm_chile['All'].index.max()
graph_chile = create_graph(tpm_chile, keywords[:9])
#wc_chile = create_wc(tpm_chile, keywords)
wc_chile = create_wc2(word_counter)
q_chile = Queue()

tpm_prensa = get_tpm(df.loc[df['screenName'].isin(noticieros)].copy(), keywords)
datetime_prensa = tpm_prensa['All'].index.max()
graph_prensa = create_graph(tpm_prensa, keywords[:9])
wc_prensa = create_wc(tpm_prensa, keywords)
q_prensa = Queue()

tpm_politicos = get_tpm(df.loc[df['screenName'].isin(politicos)].copy(), keywords)
datetime_politicos = tpm_politicos['All'].index.max()
graph_politicos = create_graph(tpm_politicos, keywords[:9])
wc_politicos = create_wc(tpm_politicos, keywords)
q_politicos = Queue()

max_length = 100  # maximum number of points to plot

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# layout
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

fig_tpm_chile = dcc.Graph(figure=graph_chile, id='plot-tweets-chile')
fig_tpm_prensa = dcc.Graph(figure=graph_prensa, id='plot-tweets-prensa')
fig_tpm_politicos = dcc.Graph(figure=graph_politicos, id='plot-tweets-politicos')

fig_wc_chile = dcc.Graph(figure=wc_chile, id='word-cloud-chile')
fig_wc_prensa = dcc.Graph(figure=wc_prensa, id='word-cloud-prensa')
fig_wc_politicos = dcc.Graph(figure=wc_politicos, id='word-cloud-politicos')

# Dash object
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# CACHE_CONFIG = {
#     'CACHE_TYPE': 'filesystem',
#     'CACHE_DIR': 'cache-directory'
# }
# cache = Cache()
# cache.init_app(app.server, config=CACHE_CONFIG)


# layout for Dash object
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

    dcc.Tabs(id='tabs-graphs', value='tab-chile', children=[
        dcc.Tab(label='Prensa', id='graphs-prensa', value='tab-prensa', children=html.Div([
            html.H6(
                children="Los distintos medios de comunicación chilenos utilizan Twitter.  En tiempo real, se puede "
                         "ver la cantidad de Tweets realizadas por la prensa:",
                style={'textAlign': 'center'}),
            html.Div(fig_tpm_prensa, style={'textAlign': 'center'}),

            html.H6("En donde las palabras que más usadas en sus tweets son:",
                    style={'textAlign': 'center'}),
            html.Div(fig_wc_prensa, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'})
        ])
                ),

        dcc.Tab(label='Chile', id='graphs-chile', value='tab-chile', children=html.Div([
            html.H6(
                children="Los chilenos también usan Twitter.  En tiempo real, se puede ver la frecuencia en que la "
                         "gente utiliza la red social para expresarse:",
                style={'textAlign': 'center'}),
            html.Div(fig_tpm_chile, style={'textAlign': 'center'}),

            html.H6("Las palabras que más usan los usuarios de twitter son:",
                    style={'textAlign': 'center'}),
            html.Div(fig_wc_chile, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'}),
        ])
                ),

        dcc.Tab(label='Politicos', id='graphs-politicos', value='tab-politicos', children=html.Div([
            html.H6(
                children="Twitter se ha vuelto una plataforma importante para los políticos de hoy.  La frecuencia "
                         "con la que publican en Twitter es:",
                style={'textAlign': 'center'}),
            html.Div(fig_tpm_politicos, style={'textAlign': 'center'}),

            html.H6("Las palabras que más usan los políticos para expresarse en Twitter son:",
                    style={'textAlign': 'center'}),
            html.Div(fig_wc_politicos, style={'textAlign': 'center', 'display': 'flex', 'justify-content': 'center'}),
        ])
                ),
    ]),

    # ======== hidden signal value ======== #
    html.Div(id='signal', style={'display': 'none'}),

    # ========  time interval ======== #
    dcc.Interval(id='interval',
                 interval=time_interval * 1000,  # in milliseconds
                 n_intervals=0),
])


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# functions
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# @cache.memoize()
# def global_store(num_limit=None):
#     """
#     Read data from mongo with cache.
#     """
#     return read_mongo('dbTweets', 'tweets_chile',
#                       query_fields={"dateTweet": 1, "tweet": 1, "screenName": 1},
#                       json_only=True, num_limit=num_limit)


def multiprocessing_wc(tpm, kws, queue, test_without_wc=True):
    """
    function that enables to create WordCloud in a different process.
    """
    queue.put(create_wc(tpm, kws))

def multiprocessing_wc2(counter, queue):
    """
    Same as  multiprocessing_wc but with the new create_wc that
    receives a counter rather than a dataframe
    :param counter: Counter() instance
    :param queue: Queue() instance
    """
    queue.put(create_wc2(counter))

def update_counter(data_frame):
    twiterator = map(process, data_frame['tweet'])
    return init_counter(twiterator)

def update_tpm(data_frame, kws, tpm, datetime, return_changed=True):
    """
    updates tweets-per-minute with new data_frame.

    Params:
        data_frame (pd.DataFrame): data of tweets.
        tpm (dict(int[:])): dictionary with tweets-per-minute for different keywords.
        kws (str[:]): list of keywords.
        datetime (Datetime): last datetime in tpm.

    Returns:
        tpm_changed (bool): bool that says if tpm changed in the process or not.
        tpm (dict(int[:])): new dictionary of tweets-per-minute.
        new_datetime (Datetime): new datetime value.
    """
    tpm_changed = False

    new_tpm = get_tpm(data_frame, keywords)

    for key in (kws + ['All']):
        # keep only new values of tweets_per_minute
        new_tpm[key] = new_tpm[key].loc[new_tpm[key].index > datetime]
        tpm_changed = len(new_tpm[key].index) > 0

        tpm[key] = tpm[key].append(new_tpm[key])
        if len(tpm[key].index) > max_length:  # check tpm array max length
            tpm[key] = tpm[key].iloc[-max_length:]

    new_datetime = tpm['All'].index.max()

    if return_changed is True:
        return tpm_changed, tpm, new_datetime
    else:
        return tpm, new_datetime


def update_tpm_users(data_frame, users, keywords, tpm, datetime, return_changed=True):
    """
    updates tweets-per-minute with new data_frame for tweets that come from certain users.

    Params:
        data_frame (pd.DataFrame): data of tweets.
        user (str[:]): list of usernames used to filter data_frame.
        tpm (dict(int[:])): dictionary with tweets-per-minute for different keywords.
        kws (str[:]): list of keywords.
        datetime (Datetime): last datetime in tpm.

    Returns:
        tpm_changed (bool): bool that says if tpm changed in the process or not.
        tpm (dict(int[:])): new dictionary of tweets-per-minute.
        new_datetime (Datetime): new datetime value.
    """
    tpm_changed = False

    df_user = data_frame.loc[data_frame['screenName'].isin(users)]
    new_tpm = get_tpm(df_user, keywords)

    for key in (keywords + ['All']):
        # keep only new values of tweets_per_minute
        new_tpm[key] = new_tpm[key].loc[new_tpm[key].index > datetime]
        tpm_changed = len(new_tpm[key].index) > 0

        tpm[key] = tpm[key].append(new_tpm[key])
        if len(tpm[key].index) > max_length:  # check tpm array max length
            tpm[key] = tpm[key].iloc[-max_length:]

    new_datetime = tpm['All'].index.max()

    if return_changed is True:
        return tpm_changed, tpm, new_datetime
    else:
        return tpm, new_datetime


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# callbacks
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
@app.callback(
    Output('signal', 'children'),
    [Input('interval', 'n_intervals')]
)
def compute_data(_):
    """
    function that will be triggerd after every "time_interval".  It reads the data from mongo and returns it.
    """
    return read_mongo('dbTweets', 'tweets_chile',
                      query_fields={"dateTweet": 1, "tweet": 1, "screenName": 1},
                      json_only=True, num_limit=10**5)

# tweets per minute callbacks
@app.callback(
    [Output('plot-tweets-chile', 'figure'), Output('word-cloud-chile', 'figure')],
    [Input('signal', 'children')]
)
def update_graphs_chile(data):
    """
    When compute_data() returns the data read from mongo.  The plot and wordcloud of "tab-chile" will be updated.
    """
    global tpm_chile, datetime_chile, wc_chile, graph_chile

    tpm_changed, tpm_chile, datetime_chile = \
        update_tpm(json_pandas(data).copy(), keywords, tpm_chile, datetime_chile)

    if tpm_changed is True:
        #p = Process(target=multiprocessing_wc, args=(tpm_chile, keywords, q_chile))
        #p.start()

        graph_chile = create_graph(tpm_chile, keywords[:9])

        #wc_chile = q_chile.get()
        #p.join()

        word_counter = update_counter(json_pandas(data).copy())

        p2 = Process(target=multiprocessing_wc2, args=(word_counter, q_chile))
        p2.start()
        wc_chile = q_chile.get()
        p2.join()

    return graph_chile, wc_chile


@app.callback(
    [Output('plot-tweets-prensa', 'figure'), Output('word-cloud-prensa', 'figure')],
    [Input('signal', 'children')]
)
def update_graphs_prensa(data):
    """
    When compute_data() returns the data read from mongo.  The plot and wordcloud of "tab-prensa" will be updated.
    """
    global tpm_prensa, datetime_prensa, wc_prensa, graph_prensa

    tpm_changed, tpm_prensa, datetime_prensa = \
        update_tpm_users(json_pandas(data).copy(), noticieros, keywords, tpm_prensa, datetime_prensa)

    if tpm_changed is True:
        p = Process(target=multiprocessing_wc, args=(tpm_prensa, keywords, q_prensa))
        p.start()

        graph_prensa = create_graph(tpm_prensa, keywords[:9])

        wc_prensa = q_prensa.get()
        p.join()

    return graph_prensa, wc_prensa


@app.callback(
    [Output('plot-tweets-politicos', 'figure'), Output('word-cloud-politicos', 'figure')],
    [Input('signal', 'children')]
)
def update_graphs_politicos(data):
    """
    When compute_data() returns the data read from mongo.  The plot and wordcloud of "tab-politicos" will be updated.
    """
    global tpm_politicos, datetime_politicos, wc_politicos, graph_politicos

    tpm_changed, tpm_politicos, datetime_politicos = \
        update_tpm_users(json_pandas(data).copy(), politicos, keywords, tpm_politicos, datetime_politicos)

    if tpm_changed is True:
        p = Process(target=multiprocessing_wc, args=(tpm_politicos, keywords, q_politicos))
        p.start()

        graph_politicos = create_graph(tpm_politicos, keywords[:9])

        wc_politicos = q_politicos.get()
        p.join()

    return graph_politicos, wc_politicos


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# main
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
if __name__ == '__main__':
    app.run_server(port=3000, debug=True)
